"""Unit, pipeline, and security guardrail tests for App Teardown & Product Research Toolkit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from app_teardown.analyzer import analyze_competitor, compute_cross_analysis, detect_product_mode
from app_teardown.asset_kit_finder import find_free_asset_kits
from app_teardown.dashboard import write_dashboard
from app_teardown.frame_extractor import (
    extract_palette_swatches,
    render_palette_card,
    select_hybrid_timestamps,
)
from app_teardown.idea_planner import decompose_idea, get_tech_profile, recommend_tech_stacks
from app_teardown.models import (
    CompetitorRecord,
    DomainEvidenceItem,
    IAPItem,
    KeyframeRecord,
    ReviewSample,
    TeardownRun,
    WebEvidenceItem,
    YouTubeVideoRecord,
)
from app_teardown.pipeline import rebuild_teardown_reports
from app_teardown.report_generator import write_campaign_reports, write_competitor_artifacts
from app_teardown.utils import (
    format_timestamp_mmss,
    parse_installs_int,
    parse_price_float,
    parse_store_target,
    safe_join,
    slugify,
    validate_asset_url,
    validate_public_web_url,
)
from app_teardown.web_researcher import _decode_ddg_redirect, build_web_research_queries
from app_teardown.youtube_harvester import build_youtube_queries, score_youtube_candidate


# --- Security Guardrail Tests ---


def test_safe_join_blocks_traversal(tmp_path: Path) -> None:
    ok = safe_join(tmp_path, "apps", "gp_demo")
    assert ok.parent.parent == tmp_path.resolve()

    for bad in ("..", "../etc", "a/b", "a\\b", "", "foo\x00bar"):
        with pytest.raises(ValueError):
            safe_join(tmp_path, bad)


def test_validate_asset_url_ssrf_and_allowlist() -> None:
    assert validate_asset_url("https://play-lh.googleusercontent.com/abc=s512").startswith("https://")
    assert validate_asset_url("http://is1-ssl.mzstatic.com/image/thumb/a.png").startswith("https://")
    assert validate_asset_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ").startswith("https://")

    for bad in (
        "file:///etc/passwd",
        "javascript:alert(1)",
        "https://127.0.0.1/secret",
        "https://169.254.169.254/latest/meta-data/",
        "https://localhost/admin",
        "https://evil.example.com/payload.png",
    ):
        with pytest.raises(ValueError):
            validate_asset_url(bad)


def test_validate_public_web_url_blocks_private_and_local() -> None:
    assert validate_public_web_url("https://sensortower.com/blog/hypercasual").startswith("https://")
    for bad in (
        "ftp://example.com/file",
        "http://127.0.0.1:8080/x",
        "https://10.0.0.1/internal",
        "https://localhost/test",
        "https://intranet.local/secret",
    ):
        with pytest.raises(ValueError):
            validate_public_web_url(bad)


# --- Parsing & Utility Tests ---


def test_slugify_turkish_and_reserved() -> None:
    assert slugify("Şahane Oyun: Çılgın Koşu!") == "sahane-oyun-cilgin-kosu"
    assert slugify("CON") == "app-item"
    assert slugify("   ") == "app-item"


def test_parse_store_target_variants() -> None:
    assert parse_store_target("https://play.google.com/store/apps/details?id=com.kiloo.subwaysurf&gl=tr") == (
        "google_play",
        "com.kiloo.subwaysurf",
        "tr",
    )
    assert parse_store_target("https://apps.apple.com/us/app/subway-surfers/id512939461") == (
        "apple_app_store",
        "512939461",
        "us",
    )
    assert parse_store_target("com.supercell.clashroyale") == ("google_play", "com.supercell.clashroyale", None)
    assert parse_store_target("id512939461") == ("apple_app_store", "512939461", None)
    assert parse_store_target("hypercasual runner") == ("query", "hypercasual runner", None)


def test_price_installs_and_timestamps() -> None:
    assert parse_price_float("$4.99") == 4.99
    assert parse_price_float("TRY 149,99") == 149.99
    assert parse_price_float("Free") is None
    assert parse_installs_int("100,000,000+") == 100_000_000
    assert format_timestamp_mmss(125.4) == "02:05"


# --- YouTube Scoring, Hybrid Timestamps & Palette Tests ---


def test_youtube_queries_and_candidate_scoring() -> None:
    g_queries = build_youtube_queries("Subway Surfers", product_mode="game")
    a_queries = build_youtube_queries("Habitica", product_mode="app")
    assert any("gameplay" in q.lower() for q in g_queries)
    assert any("walkthrough" in q.lower() for q in a_queries)

    good = {
        "title": "Subway Surfers Mobile Gameplay No Commentary iOS Android",
        "duration": 480,
        "view_count": 250000,
        "is_live": False,
    }
    bad_mod = {
        "title": "Subway Surfers MOD APK Hack Unlimited Coins #shorts",
        "duration": 35,
        "view_count": 5000,
        "is_live": False,
    }
    live = {"title": "Subway Surfers Live Stream", "duration": 0, "view_count": 100, "is_live": True}
    assert score_youtube_candidate(good, "Subway Surfers", "game") > score_youtube_candidate(bad_mod, "Subway Surfers", "game")
    assert score_youtube_candidate(live, "Subway Surfers", "game") < 0


def test_hybrid_timestamp_selection() -> None:
    ts_list = select_hybrid_timestamps(
        duration_sec=240.0,
        scene_timestamps=[8.2, 19.5, 21.0, 54.0, 95.3, 140.0, 190.4],
        max_frames=16,
        min_gap_sec=3.5,
    )
    assert len(ts_list) == 16
    assert ts_list == sorted(ts_list, key=lambda x: x[0])
    # Scene changes should be represented alongside interval fills
    sources = {src for _, src in ts_list}
    assert "scene_change" in sources
    assert "interval" in sources


def test_palette_extraction_and_card_render(tmp_path: Path) -> None:
    img1 = Image.new("RGB", (120, 120), (255, 100, 30))
    img2 = Image.new("RGB", (120, 120), (20, 40, 90))
    swatches = extract_palette_swatches([img1, img2], top_k=4)
    assert len(swatches) >= 2
    assert all(s.hex.startswith("#") and len(s.hex) == 7 for s in swatches)

    card_path = tmp_path / "palette.png"
    assert render_palette_card(swatches, "Test Game", card_path) is True
    assert card_path.exists() and card_path.stat().st_size > 100


def test_ddg_redirect_decoder_and_web_queries() -> None:
    raw = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fsensortower.com%2Fblog%2Ftest"
    assert _decode_ddg_redirect(raw) == "https://sensortower.com/blog/test"
    gq = build_web_research_queries("Royal Match", "game")
    aq = build_web_research_queries("Duolingo", "app")
    assert len(gq) >= 3
    assert any(cat == "monetization_ads" for cat, _ in aq)


# --- Analyzer, Report Generator, Dashboard & Rebuild End-to-End Tests ---


def test_analyzer_reports_dashboard_and_rebuild(tmp_path: Path) -> None:
    assert detect_product_mode(query="hypercasual runner", category="Action") == "game"
    assert detect_product_mode(query="habit tracker", category="Productivity") == "app"

    run_dir = tmp_path / "2026-11-27_1200_demo"
    app_dir = run_dir / "apps" / "gp_hyper-dash_com-demo-dash"
    app_dir.mkdir(parents=True, exist_ok=True)

    rec = CompetitorRecord(
        store="google_play",
        app_id="com.demo.dash",
        folder_name="gp_hyper-dash_com-demo-dash",
        store_url="https://play.google.com/store/apps/details?id=com.demo.dash",
        title="Hyper Dash <script>alert(1)</script>",
        subtitle_or_short_desc="Fast 3D runner with daily rewards",
        description="Run, dodge obstacles, claim daily rewards, unlock skins, battle pass, watch ad for 2x reward, remove ads pack available.",
        developer="Demo Studio",
        category="Arcade",
        rating=4.5,
        ratings_count=125000,
        installs="10,000,000+",
        min_installs=10_000_000,
        offers_iap=True,
        iap_price_range="$1.99 - $49.99",
        iap_items=[
            IAPItem(name="Remove Ads", price="$2.99", numeric_price=2.99, tier="remove_ads"),
            IAPItem(name="Season Pass", price="$9.99", numeric_price=9.99, tier="pass"),
        ],
        ad_supported=True,
        reviews=[
            ReviewSample(rating=2, text="Super addictive gameplay but too many ads after every level!"),
            ReviewSample(rating=5, text="Very satisfying controls and smooth feel."),
        ],
        youtube_videos=[
            YouTubeVideoRecord(
                video_id="abc123",
                title="Hyper Dash Gameplay",
                url="https://www.youtube.com/watch?v=abc123",
                downloaded=True,
                clip_duration_sec=180.0,
                frames=[
                    KeyframeRecord(
                        index=1,
                        timestamp_sec=3.0,
                        timestamp_label="00:03",
                        source="interval",
                        phase_hint="ftue_launch",
                        local_path="assets/gameplay_frames/frame_01.jpg",
                        dominant_colors=["#FF6600"],
                    )
                ],
            )
        ],
        web_evidence=[
            WebEvidenceItem(
                evidence_id="EV-WEB-01",
                category="monetization_ads",
                query="Hyper Dash monetization",
                title="Hyper Dash Teardown",
                url="https://example.com/teardown",
                domain="example.com",
                snippet="Hybrid monetization with rewarded video and $2.99 no-ads pack.",
            )
        ],
    )

    sig = analyze_competitor(rec, explicit_mode="auto", query="hypercasual runner")
    assert sig.product_mode == "game"
    assert sig.has_remove_ads is True
    assert sig.has_battle_pass is True
    assert "rewarded_video" in sig.detected_ad_formats
    assert "interstitial" in sig.detected_ad_formats
    assert "excessive_ads" in sig.ux_friction_themes
    assert sig.ad_complaint_ratio_pct == 50.0
    assert sig.evidence_score >= 60

    write_competitor_artifacts(rec, app_dir)
    assert (app_dir / "teardown_report.md").exists()
    assert (app_dir / "evidence.json").exists()
    assert (app_dir / "web_research.md").exists()
    assert (app_dir / "store_metadata.md").exists()

    ledger = json.loads((app_dir / "evidence.json").read_text(encoding="utf-8"))
    ev_ids = {item["evidence_id"] for item in ledger["items"]}
    assert "EV-STORE-01" in ev_ids
    assert "EV-FRAME-01-01" in ev_ids
    assert "EV-WEB-01" in ev_ids

    run = TeardownRun(
        run_id="2026-11-27_1200_demo",
        campaign_name="demo",
        query="hypercasual runner",
        product_mode="game",
        stores=["google_play"],
        country="us",
        lang="en",
        limit_per_store=5,
        max_video_sec=240,
        max_frames=24,
        created_at="2026-11-27T12:00:00+00:00",
        output_dir=str(run_dir),
        competitors=[rec],
        cross_analysis=compute_cross_analysis([rec]),
    )
    write_campaign_reports(run, run_dir)
    dash_path = write_dashboard(run, run_dir)

    assert (run_dir / "GENEL_TEARDOWN_RAPORU.md").exists()
    assert (run_dir / "TASARIM_BLUEPRINT.md").exists()
    assert (run_dir / "apps_index.csv").exists()
    assert dash_path.exists()

    # XSS & CSP verification on dashboard.html and dashboard.js
    html_text = dash_path.read_text(encoding="utf-8")
    js_text = (run_dir / "dashboard.js").read_text(encoding="utf-8")
    assert "Content-Security-Policy" in html_text
    assert "<script>alert(1)</script>" not in html_text
    assert "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e" in html_text
    assert "innerHTML" not in js_text

    # Rebuild from saved metadata.json
    rebuilt = rebuild_teardown_reports(run_dir)
    assert len(rebuilt.competitors) == 1
    assert rebuilt.competitors[0].app_id == "com.demo.dash"


# --- Idea Intake, Tech Advisor, Domain Research & Free Kit Finder Tests ---


def test_idea_decomposition_splits_mechanic_vs_domain_and_recommends_godot() -> None:
    brief = decompose_idea(
        idea="Kapılardan geçtiğin yemek yapma oyunu istiyorum, hypercasual hamburger dizilimi",
        product_mode="auto",
        selected_tech="godot",
    )
    assert brief.product_mode == "game"
    assert "hypercasual" in brief.mechanic_query.lower()
    assert "runner" in brief.mechanic_query.lower() or "gate" in brief.mechanic_query.lower()
    assert "burger" in brief.theme_label.lower() or "food" in brief.theme_label.lower()
    assert any("hamburger" in t.lower() or "layers" in t.lower() for t in brief.domain_topics)
    assert brief.selected_tech == "godot"
    assert len(brief.tech_options) == 3
    assert brief.tech_options[0].id == "godot"
    assert brief.tech_options[0].recommended is True


def test_app_mode_tech_recommendations_and_free_kits() -> None:
    opts = recommend_tech_stacks("Günlük alışkanlık ve su takip uygulaması", product_mode="app")
    assert opts[0].id == "flutter"
    assert get_tech_profile("godot4") is not None
    assert get_tech_profile("expo").id == "react-native"

    game_kits = find_free_asset_kits(
        product_mode="game",
        selected_tech="godot",
        theme_label="burger cooking food",
        run_live_web_search=False,
    )
    categories = {k.category for k in game_kits}
    assert {"ui_ux", "models_sprites", "audio_sfx", "fonts", "engine_sdk"}.issubset(categories)
    assert any("Food Kit" in k.name for k in game_kits)
    assert any("AdMob" in k.name or "Godot" in k.name for k in game_kits)


def test_domain_kits_and_blueprint_reports_with_rebuild(tmp_path: Path) -> None:
    run_dir = tmp_path / "2026-11-27_1300_burger-godot"
    (run_dir / "apps").mkdir(parents=True, exist_ok=True)
    brief = decompose_idea(
        idea="Kapılardan geçtiğin hypercasual hamburger yapma oyunu",
        product_mode="game",
        selected_tech="godot",
    )
    kits = find_free_asset_kits("game", "godot", "burger cooking food", run_live_web_search=False)
    dom_ev = [
        DomainEvidenceItem(
            evidence_id="EV-DOM-01",
            topic="classic hamburger layers assembly order",
            query="classic hamburger layers assembly order",
            title="Perfect Burger Layer Order",
            url="https://example.com/burger-layers",
            domain="example.com",
            snippet="Bottom bun, sauce, lettuce barrier, patty, melted cheese, tomato, pickles, top bun.",
        )
    ]
    run = TeardownRun(
        run_id="2026-11-27_1300_burger-godot",
        campaign_name="burger-godot",
        query=brief.mechanic_query,
        product_mode="game",
        stores=["google_play"],
        country="us",
        lang="en",
        limit_per_store=5,
        max_video_sec=240,
        max_frames=24,
        created_at="2026-11-27T13:00:00+00:00",
        output_dir=str(run_dir),
        idea_brief=brief,
        domain_evidence=dom_ev,
        free_asset_kits=kits,
        competitors=[],
        cross_analysis={"total_competitors": 0, "dominant_mode": "game"},
    )
    write_campaign_reports(run, run_dir)
    dash = write_dashboard(run, run_dir)

    assert (run_dir / "DOMAIN_ARASTIRMASI.md").exists()
    assert (run_dir / "FREE_ASSET_VE_KIT_REHBERI.md").exists()
    assert (run_dir / "evidence" / "domain_sources.json").exists()
    assert (run_dir / "evidence" / "free_kits.json").exists()
    bp_text = (run_dir / "TASARIM_BLUEPRINT.md").read_text(encoding="utf-8")
    assert "Godot 4" in bp_text
    assert "Kenney Food Kit" in bp_text
    assert "DOMAIN_ARASTIRMASI.md" in bp_text
    assert dash.exists()
    assert "kits-grid" in dash.read_text(encoding="utf-8")

    # Rebuild preserves idea_brief, domain_evidence, and free_asset_kits
    rebuilt = rebuild_teardown_reports(run_dir)
    assert rebuilt.idea_brief is not None
    assert rebuilt.idea_brief.selected_tech == "godot"
    assert len(rebuilt.domain_evidence) == 1
    assert len(rebuilt.free_asset_kits) == len(kits)

