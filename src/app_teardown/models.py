"""Data models for App Teardown & Product Research runs, idea intake, domain research, free kits, frames, and palettes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TechStackOption:
    id: str  # godot, unity, unreal, phaser, flutter, react-native, swiftui-kotlin
    name: str
    recommended: bool = False
    complexity: str = "Medium"  # Low, Medium, High
    license_cost: str = "Free / Open Source"
    best_for: str = ""
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    asset_formats: list[str] = field(default_factory=list)
    architecture_notes: list[str] = field(default_factory=list)


@dataclass
class IdeaBrief:
    raw_idea: str = ""
    product_mode: str = "game"  # game | app
    mechanic_query: str = ""    # Used for store competitor benchmarking (e.g. "hypercasual gate runner")
    theme_label: str = ""       # Used for free asset kit & domain search (e.g. "burger cooking food")
    core_subject: str = ""      # Concrete real-world subject (e.g. "hamburger", "espresso coffee", "luxury perfume")
    famous_brands: list[str] = field(default_factory=list)  # Real-world iconic brands/products to benchmark visually
    domain_topics: list[str] = field(default_factory=list)  # Subject-matter research queries
    image_queries: list[dict[str, str]] = field(default_factory=list)  # Structured visual reference search specs
    selected_tech: str = ""     # Chosen tech stack ID (e.g. "godot", "unity", "flutter")
    tech_options: list[TechStackOption] = field(default_factory=list)


@dataclass
class DomainEvidenceItem:
    evidence_id: str = ""       # EV-DOM-01
    topic: str = ""
    query: str = ""
    title: str = ""
    url: str = ""
    domain: str = ""
    snippet: str = ""
    fetched_at: str = ""
    category: str = "general"   # what_is_it | how_its_made | anatomy_layers | famous_brands | real_world_equivalent | general
    source_engine: str = "duckduckgo"  # wikipedia | duckduckgo | web_search


@dataclass
class DomainReferenceImage:
    evidence_id: str = ""       # EV-REF-01
    category: str = "real_world_equivalent"  # anatomy_layers | how_its_made | real_world_equivalent | famous_brand
    subject_label: str = ""     # e.g. "McDonald's Big Mac", "Hamburger Layers Anatomy"
    query: str = ""
    title: str = ""
    source_engine: str = ""     # bing_images | wikimedia_commons | wikipedia | openverse
    source_url: str = ""        # Direct image URL downloaded
    page_url: str = ""          # Originating web page citation URL
    domain: str = ""
    license_note: str = "Visual reference only (verify rights; do not copy trademarked logos or brand photography)"
    local_path: str = ""        # Relative to run_dir
    width: int = 0
    height: int = 0
    image_format: str = ""
    file_size_bytes: int = 0
    dominant_colors: list[str] = field(default_factory=list)
    downloaded: bool = False
    error: str = ""


@dataclass
class AssetKitItem:
    evidence_id: str = ""       # EV-KIT-01
    category: str = "ui_ux"     # ui_ux, models_sprites, audio_sfx, fonts, engine_sdk
    name: str = ""
    source: str = ""            # e.g. Kenney.nl, Quaternius, Figma Community, Freesound
    url: str = ""
    license: str = "CC0 / Free"
    formats: list[str] = field(default_factory=list)
    tech_fit: list[str] = field(default_factory=list)
    usage_note: str = ""
    discovery_origin: str = "curated"  # curated | web_search


@dataclass
class ReviewSample:
    author: str = ""
    rating: int = 0
    title: str = ""
    text: str = ""
    date: str = ""
    version: str = ""
    thumbs_up: int = 0
    developer_reply: str = ""


@dataclass
class IAPItem:
    name: str
    price: str = ""
    numeric_price: float | None = None
    tier: str = "other"  # micro, starter, mid, whale, subscription, remove_ads, pass, other


@dataclass
class ColorSwatch:
    hex: str
    rgb: tuple[int, int, int] = (0, 0, 0)
    ratio_pct: float = 0.0
    luminance: float = 0.0
    temperature: str = "neutral"  # warm, cool, neutral


@dataclass
class ImageAsset:
    kind: str
    source_url: str = ""
    local_path: str = ""
    width: int = 0
    height: int = 0
    orientation: str = ""
    aspect_ratio: str = ""
    image_format: str = ""
    file_size_bytes: int = 0
    dominant_colors: list[str] = field(default_factory=list)
    downloaded: bool = False
    error: str = ""


@dataclass
class KeyframeRecord:
    index: int
    timestamp_sec: float
    timestamp_label: str
    source: str = "interval"  # scene_change, interval
    phase_hint: str = "early_core"  # ftue_launch, early_core, mid_loop, late_monetization_meta
    local_path: str = ""
    width: int = 0
    height: int = 0
    dominant_colors: list[str] = field(default_factory=list)
    avg_brightness: float = 0.0


@dataclass
class YouTubeVideoRecord:
    video_id: str = ""
    title: str = ""
    channel: str = ""
    duration_sec: float = 0.0
    view_count: int = 0
    upload_date: str = ""
    url: str = ""
    search_query: str = ""
    selection_score: float = 0.0
    downloaded: bool = False
    local_path: str = ""
    clip_duration_sec: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    file_size_bytes: int = 0
    frames: list[KeyframeRecord] = field(default_factory=list)
    storyboard_paths: list[str] = field(default_factory=list)
    palette_card_path: str = ""
    dominant_colors: list[ColorSwatch] = field(default_factory=list)
    error: str = ""


@dataclass
class WebEvidenceItem:
    evidence_id: str = ""
    category: str = "general"  # revenue_downloads, monetization_ads, retention_ux, gameplay_design
    query: str = ""
    title: str = ""
    url: str = ""
    domain: str = ""
    snippet: str = ""
    fetched_at: str = ""


@dataclass
class ProductSignals:
    product_mode: str = "game"  # game | app
    monetization_model: str = "Freemium"
    detected_ad_formats: list[str] = field(default_factory=list)
    iap_tiers: dict[str, int] = field(default_factory=dict)
    iap_price_min: float | None = None
    iap_price_max: float | None = None
    has_subscription: bool = False
    has_remove_ads: bool = False
    has_battle_pass: bool = False
    retention_hooks: list[str] = field(default_factory=list)
    ux_friction_themes: dict[str, int] = field(default_factory=dict)
    praise_themes: dict[str, int] = field(default_factory=dict)
    ad_complaint_ratio_pct: float = 0.0
    paywall_complaint_ratio_pct: float = 0.0
    popularity_score: float = 0.0
    evidence_score: int = 0


@dataclass
class CompetitorRecord:
    store: str  # google_play | apple_app_store
    app_id: str
    folder_name: str
    product_mode: str = "game"
    country: str = "us"
    lang: str = "en"
    store_url: str = ""
    title: str = ""
    subtitle_or_short_desc: str = ""
    description: str = ""
    developer: str = ""
    category: str = ""
    secondary_categories: list[str] = field(default_factory=list)
    rating: float = 0.0
    ratings_count: int = 0
    reviews_count: int = 0
    installs: str = ""
    min_installs: int = 0
    price: float = 0.0
    currency: str = "USD"
    free: bool = True
    offers_iap: bool = False
    iap_price_range: str = ""
    iap_items: list[IAPItem] = field(default_factory=list)
    ad_supported: bool | None = None
    content_rating: str = ""
    version: str = ""
    released_date: str = ""
    last_updated: str = ""
    whats_new: str = ""
    icon_url: str = ""
    screenshot_urls: list[str] = field(default_factory=list)
    store_video_urls: list[str] = field(default_factory=list)
    reviews: list[ReviewSample] = field(default_factory=list)
    icon_asset: ImageAsset | None = None
    screenshots: list[ImageAsset] = field(default_factory=list)
    screenshots_sheet_path: str = ""
    youtube_videos: list[YouTubeVideoRecord] = field(default_factory=list)
    web_evidence: list[WebEvidenceItem] = field(default_factory=list)
    combined_palette: list[ColorSwatch] = field(default_factory=list)
    palette_card_path: str = ""
    signals: ProductSignals = field(default_factory=ProductSignals)
    fetched_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TeardownRun:
    run_id: str
    campaign_name: str
    query: str
    product_mode: str  # auto | game | app
    stores: list[str]
    country: str
    lang: str
    limit_per_store: int
    max_video_sec: int
    max_frames: int
    created_at: str
    output_dir: str
    official_only: bool = False
    idea_brief: IdeaBrief | None = None
    domain_evidence: list[DomainEvidenceItem] = field(default_factory=list)
    domain_references: list[DomainReferenceImage] = field(default_factory=list)
    domain_reference_sheet_path: str = ""
    domain_palette: list[ColorSwatch] = field(default_factory=list)
    domain_palette_card_path: str = ""
    free_asset_kits: list[AssetKitItem] = field(default_factory=list)
    competitors: list[CompetitorRecord] = field(default_factory=list)
    cross_analysis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
