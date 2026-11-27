"""Unit, pipeline, and security guardrail tests for App Teardown & Product Research Toolkit."""

from __future__ import annotations

from io import BytesIO
import json
import socket
from pathlib import Path

import pytest
from PIL import Image

from app_teardown.analyzer import analyze_competitor, compute_cross_analysis, detect_product_mode
from app_teardown.asset_kit_finder import find_free_asset_kits
from app_teardown.cli import build_parser
from app_teardown.dashboard import write_dashboard
from app_teardown.domain_researcher import (
    _save_verified_reference_image,
    build_domain_reference_sheet,
    classify_domain_category,
)
from app_teardown.frame_extractor import (
    extract_palette_swatches,
    render_palette_card,
    select_hybrid_timestamps,
)
from app_teardown.idea_planner import (
    build_domain_image_queries,
    decompose_idea,
    extract_core_subject,
    get_tech_profile,
    recommend_tech_stacks,
)
from app_teardown.models import (
    ColorSwatch,
    CompetitorRecord,
    DomainEvidenceItem,
    DomainReferenceImage,
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
    validate_public_image_url,
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
    img1 = Image.new("RGB", (180, 100), (255, 100, 30))
    img2 = Image.new("RGB", (100, 180), (20, 40, 90))
    swatches = extract_palette_swatches([img1, img2], top_k=4)
    assert len(swatches) >= 2
    assert all(s.hex.startswith("#") and len(s.hex) == 7 for s in swatches)
    # Non-square images must not introduce artificial black (#000000) mosaic padding
    assert all(s.hex != "#000000" for s in swatches)

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
    assert (run_dir / "PROTOTIP_VE_TAM_SURUM_PLANI.md").exists()
    assert (run_dir / "evidence" / "domain_sources.json").exists()
    assert (run_dir / "evidence" / "free_kits.json").exists()
    bp_text = (run_dir / "TASARIM_BLUEPRINT.md").read_text(encoding="utf-8")
    assert "Godot 4" in bp_text
    assert "Kenney Food Kit" in bp_text
    assert "DOMAIN_ARASTIRMASI.md" in bp_text
    proto_text = (run_dir / "PROTOTIP_VE_TAM_SURUM_PLANI.md").read_text(encoding="utf-8")
    assert "Hızlı Prototip Kapsamı" in proto_text
    assert "Tam Sürümde Eklenecekler" in proto_text
    assert "Kullanıcı Geri Bildirim & Revizyon Kapısı" in proto_text
    assert "her şey tamam, yap" in proto_text
    assert dash.exists()
    dash_js = (run_dir / "dashboard.js").read_text(encoding="utf-8")
    assert "PROTOTIP_VE_TAM_SURUM_PLANI.md" in dash_js
    assert "kits-grid" in dash.read_text(encoding="utf-8")

    # Rebuild preserves idea_brief, domain_evidence, and free_asset_kits
    rebuilt = rebuild_teardown_reports(run_dir)
    assert rebuilt.idea_brief is not None
    assert rebuilt.idea_brief.selected_tech == "godot"
    assert len(rebuilt.domain_evidence) == 1
    assert len(rebuilt.free_asset_kits) == len(kits)


# --- Real-World Subject, Famous Brands & Visual Reference Tests ---


def test_validate_public_image_url_blocks_svg_and_private_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    assert validate_public_image_url("https://example.com/photos/burger.jpg", resolve_dns=False).startswith("https://")
    assert validate_public_image_url("https://ts2.mm.bing.net/th?id=OIP.abc", resolve_dns=False).startswith("https://")

    for bad in (
        "https://example.com/vector.svg",
        "https://example.com/page.html",
        "https://127.0.0.1/img.png",
        "https://localhost/img.jpg",
        "https://internal.local/img.png",
        "file:///C:/Windows/win.ini",
    ):
        with pytest.raises(ValueError):
            validate_public_image_url(bad, resolve_dns=False)

    # DNS resolution returning private / cloud metadata IP must be rejected
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 0))],
    )
    with pytest.raises(ValueError, match="Non-global IP blocked"):
        validate_public_image_url("https://rebind.example.com/photo.jpg", resolve_dns=True)

    # DNS resolution returning global public IP passes
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )
    assert validate_public_image_url("https://public.example.com/photo.jpg", resolve_dns=True) == "https://public.example.com/photo.jpg"


def test_real_world_subject_famous_brands_and_dynamic_extraction() -> None:
    # 1. Built-in burger profile
    burger = decompose_idea("Kapılardan geçtiğin burger yapma oyunu istiyorum", selected_tech="godot")
    assert burger.core_subject == "hamburger"
    assert any("Big Mac" in b for b in burger.famous_brands)
    assert any("Whopper" in b for b in burger.famous_brands)
    img_cats = {q["category"] for q in burger.image_queries}
    assert {"anatomy_layers", "how_its_made", "real_world_equivalent", "famous_brand"}.issubset(img_cats)

    # 2. Dynamic extraction for an unseen custom idea
    custom_subj = extract_core_subject("Çiçek dükkanı tycoon mobil oyun istiyorum")
    assert "çiçek" in custom_subj.lower()
    flower = decompose_idea("Flower shop boutique tycoon mobile game")
    assert "flower" in flower.core_subject.lower()
    assert len(flower.domain_topics) == 4
    assert any("what is" in t.lower() for t in flower.domain_topics)
    assert any("how " in t.lower() for t in flower.domain_topics)
    assert any("layers" in t.lower() or "anatomy" in t.lower() for t in flower.domain_topics)
    assert any("famous" in t.lower() for t in flower.domain_topics)

    # 3. Explicit subject + famous brands override
    explicit = decompose_idea(
        "My custom craft game",
        explicit_subject="taco",
        explicit_famous_brands=["Taco Bell Crunchwrap", "Chipotle Street Taco"],
    )
    assert explicit.core_subject == "taco"
    assert explicit.famous_brands == ["Taco Bell Crunchwrap", "Chipotle Street Taco"]
    q_list = build_domain_image_queries("taco", famous_brands=explicit.famous_brands)
    assert any(q["label"] == "Taco Bell Crunchwrap" and q["category"] == "famous_brand" for q in q_list)


def test_domain_category_classification_reference_sheet_and_dashboard_rebuild(tmp_path: Path) -> None:
    assert classify_domain_category("what is a hamburger real world definition") == "what_is_it"
    assert classify_domain_category("how a hamburger is made grilling stages") == "how_its_made"
    assert classify_domain_category("classic hamburger layers assembly order") == "anatomy_layers"
    assert classify_domain_category("McDonald's Big Mac vs Burger King Whopper") == "famous_brands"

    run_dir = tmp_path / "2026-11-27_1800_burger-refs"
    refs_dir = run_dir / "assets" / "domain_references"
    (run_dir / "apps").mkdir(parents=True, exist_ok=True)

    # Small image must be rejected (< 120px)
    tiny_buf = BytesIO()
    Image.new("RGB", (60, 60), (200, 100, 50)).save(tiny_buf, format="PNG")
    with pytest.raises(ValueError, match="Image too small"):
        _save_verified_reference_image(tiny_buf.getvalue(), refs_dir, "ref_tiny", run_dir)

    # Valid images saved, verified, sheet composed, and palette rendered
    buf1 = BytesIO()
    Image.new("RGB", (320, 240), (216, 146, 59)).save(buf1, format="JPEG")
    _, w1, h1, fmt1, sz1, hex1, fp1 = _save_verified_reference_image(buf1.getvalue(), refs_dir, "ref_01_brand_big-mac", run_dir)
    assert (w1, h1, fmt1) == (320, 240, "JPEG")
    assert sz1 > 0 and len(hex1) >= 1 and len(fp1) == 16

    buf2 = BytesIO()
    Image.new("RGB", (300, 300), (86, 154, 50)).save(buf2, format="PNG")
    _, w2, h2, fmt2, sz2, hex2, fp2 = _save_verified_reference_image(buf2.getvalue(), refs_dir, "ref_02_anatomy_layers", run_dir)
    assert fp1 != fp2

    refs = [
        DomainReferenceImage(
            evidence_id="EV-REF-01",
            category="famous_brand",
            subject_label="McDonald's Big Mac <script>alert(1)</script>",
            query="McDonald's Big Mac product photo",
            title="Big Mac",
            source_engine="bing_images",
            source_url="https://example.com/bigmac.jpg",
            page_url="https://example.com/bigmac",
            domain="example.com",
            local_path="assets/domain_references/ref_01_brand_big-mac.jpg",
            width=w1,
            height=h1,
            image_format=fmt1,
            file_size_bytes=sz1,
            dominant_colors=hex1,
            downloaded=True,
        ),
        DomainReferenceImage(
            evidence_id="EV-REF-02",
            category="anatomy_layers",
            subject_label="Hamburger Katman Anatomisi",
            query="hamburger layers diagram",
            title="Burger Layers",
            source_engine="wikimedia_commons",
            source_url="https://commons.wikimedia.org/wiki/File:Burger.jpg",
            page_url="https://commons.wikimedia.org/wiki/File:Burger.jpg",
            domain="commons.wikimedia.org",
            local_path="assets/domain_references/ref_02_anatomy_layers.jpg",
            width=w2,
            height=h2,
            image_format=fmt2,
            file_size_bytes=sz2,
            dominant_colors=hex2,
            downloaded=True,
        ),
    ]

    sheet_rel = build_domain_reference_sheet(
        refs,
        run_dir=run_dir,
        output_path=refs_dir / "domain_reference_sheet.png",
        subject_title="hamburger",
    )
    assert sheet_rel == "assets/domain_references/domain_reference_sheet.png"
    assert (run_dir / sheet_rel).exists()

    pal_swatches = [ColorSwatch(hex="#D8923B", rgb=(216, 146, 59), ratio_pct=60.0, luminance=0.58, temperature="warm")]
    pal_card_path = refs_dir / "domain_palette_card.png"
    assert render_palette_card(pal_swatches, "Real-World Burger", pal_card_path) is True

    brief = decompose_idea("Hypercasual hamburger gate runner", product_mode="game", selected_tech="godot")
    run = TeardownRun(
        run_id="2026-11-27_1800_burger-refs",
        campaign_name="burger-refs",
        query=brief.mechanic_query,
        product_mode="game",
        stores=["google_play"],
        country="us",
        lang="en",
        limit_per_store=5,
        max_video_sec=240,
        max_frames=24,
        created_at="2026-11-27T18:00:00+00:00",
        output_dir=str(run_dir),
        idea_brief=brief,
        domain_evidence=[
            DomainEvidenceItem(
                evidence_id="EV-DOM-01",
                topic="hamburger",
                query="hamburger",
                title="Hamburger (Wikipedia)",
                url="https://en.wikipedia.org/wiki/Hamburger",
                domain="en.wikipedia.org",
                snippet="A hamburger is a sandwich consisting of a cooked beef patty inside a sliced bun.",
                category="what_is_it",
                source_engine="wikipedia",
            )
        ],
        domain_references=refs,
        domain_reference_sheet_path=sheet_rel,
        domain_palette=pal_swatches,
        domain_palette_card_path="assets/domain_references/domain_palette_card.png",
        competitors=[],
        cross_analysis={"total_competitors": 0, "dominant_mode": "game"},
    )
    write_campaign_reports(run, run_dir)
    dash = write_dashboard(run, run_dir)

    dom_md = (run_dir / "DOMAIN_ARASTIRMASI.md").read_text(encoding="utf-8")
    assert "EV-REF-01" in dom_md
    assert "domain_reference_sheet.png" in dom_md
    assert "Nedir & Gerçek Hayat Karşılığı" in dom_md
    assert "Ünlü Markalar İncelemesi" in dom_md
    assert (run_dir / "evidence" / "domain_references.json").exists()

    html_text = dash.read_text(encoding="utf-8")
    js_text = (run_dir / "dashboard.js").read_text(encoding="utf-8")
    assert "domain-refs-grid" in html_text
    assert "ref-cat-filter" in html_text
    assert "<script>alert(1)</script>" not in html_text
    assert "innerHTML" not in js_text

    # Rebuild preserves all visual reference fields and famous brands
    rebuilt = rebuild_teardown_reports(run_dir)
    assert len(rebuilt.domain_references) == 2
    assert rebuilt.domain_reference_sheet_path == sheet_rel
    assert rebuilt.domain_palette_card_path == "assets/domain_references/domain_palette_card.png"
    assert len(rebuilt.domain_palette) == 1
    assert rebuilt.idea_brief is not None and rebuilt.idea_brief.core_subject == "hamburger"


def test_cli_parser_supports_new_subject_and_brand_flags() -> None:
    parser = build_parser()
    td_args = parser.parse_args([
        "teardown",
        "--idea", "burger gate runner",
        "--subject", "hamburger",
        "--famous-brands", "McDonald's Big Mac", "Burger King Whopper",
        "--max-domain-images", "8",
    ])
    assert td_args.subject == "hamburger"
    assert td_args.famous_brands == ["McDonald's Big Mac", "Burger King Whopper"]
    assert td_args.max_domain_images == 8

    dom_args = parser.parse_args([
        "research-domain",
        "--idea", "burger oyunu",
        "--brands", "McDonald's Big Mac", "Shake Shack",
        "--out-dir", "teardowns/demo",
        "--max-images", "6",
    ])
    assert dom_args.idea == "burger oyunu"
    assert dom_args.brands == ["McDonald's Big Mac", "Shake Shack"]
    assert dom_args.max_images == 6


def test_app_mode_prototype_and_full_release_plan_generation(tmp_path: Path) -> None:
    run_dir = tmp_path / "2026-11-27_1900_habit-flutter"
    (run_dir / "apps").mkdir(parents=True, exist_ok=True)
    brief = decompose_idea("Günlük alışkanlık ve su takip uygulaması", product_mode="app", selected_tech="flutter")
    run = TeardownRun(
        run_id="2026-11-27_1900_habit-flutter",
        campaign_name="habit-flutter",
        query=brief.mechanic_query,
        product_mode="app",
        stores=["apple_app_store"],
        country="us",
        lang="en",
        limit_per_store=5,
        max_video_sec=240,
        max_frames=24,
        created_at="2026-11-27T19:00:00+00:00",
        output_dir=str(run_dir),
        idea_brief=brief,
        competitors=[],
        cross_analysis={"total_competitors": 0, "dominant_mode": "app"},
    )
    write_campaign_reports(run, run_dir)
    proto_md = (run_dir / "PROTOTIP_VE_TAM_SURUM_PLANI.md").read_text(encoding="utf-8")
    assert "Flutter (Dart)" in proto_md
    assert "Kısa Onboarding" in proto_md
    assert "Paywall" in proto_md
    assert "her şey tamam, yap" in proto_md



