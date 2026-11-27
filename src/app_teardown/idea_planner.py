"""Idea intake, mechanic-vs-theme decomposition, tech stack advisor, and subject-matter domain research."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from .analyzer import detect_product_mode
from .models import DomainEvidenceItem, IdeaBrief, TechStackOption
from .web_researcher import search_duckduckgo_html

# Engine / Framework catalog with architecture blueprints and trade-offs
TECH_PROFILES: dict[str, TechStackOption] = {
    "godot": TechStackOption(
        id="godot",
        name="Godot 4 (GDScript / C#)",
        recommended=True,
        complexity="Low",
        license_cost="100% Free (MIT, zero royalties)",
        best_for="Hypercasual, hybridcasual, 2D/3D stylized mobile games, rapid prototyping",
        pros=[
            "Ultra-lightweight editor & small mobile APK/IPA build size (<25 MB base)",
            "Zero royalties or seat fees (MIT license)",
            "Fast node/scene composition (Area3D gates, CharacterBody3D, CanvasLayer HUD, Tween juice)",
            "Native glTF/GLB 3D workflow and clean GDScript iteration speed",
        ],
        cons=[
            "Smaller commercial ad-mediation ecosystem than Unity (requires community AdMob/AppLovin plugins)",
            "Complex 3D AAA rendering lags behind Unreal",
        ],
        asset_formats=[".glb / .gltf (3D)", ".png / .svg (2D/UI)", ".ogg / .wav (Audio)", ".ttf / .otf (Fonts)"],
        architecture_notes=[
            "Root scene: Main.tscn (StateMachine: Boot -> Lobby -> Gameplay -> ResultOverlay)",
            "Runner/Core node: CharacterBody3D + StackContainer (Node3D) + Area3D GateTrigger",
            "Data-driven content: Custom Resource (.tres) definitions for recipes/layers/levels",
            "UI/UX: CanvasLayer -> MarginContainer (SafeArea inset) + Control anchor presets + event-driven signals",
            "Monetization: Poing Studios AdMob plugin (Banner/Interstitial/Rewarded) + Godot Google Play Billing / iOS StoreKit",
        ],
    ),
    "unity": TechStackOption(
        id="unity",
        name="Unity 6 LTS (C#)",
        recommended=False,
        complexity="Medium",
        license_cost="Free up to $200K revenue (Personal tier)",
        best_for="Commercial hypercasual/hybridcasual games relying heavily on ad mediation & publisher SDKs",
        pros=[
            "Industry-standard hypercasual SDK support (AppLovin MAX, ironSource/LevelPlay, Adjust, Firebase)",
            "Huge Asset Store & DOTween/Cinemachine/URP mobile polish ecosystem",
            "Easy handoff to mobile game publishers (Voodoo, Supersonic, Homa)",
        ],
        cons=[
            "Heavier editor, slower iteration & larger baseline binary size than Godot",
            "Commercial licensing thresholds above $200K annual revenue",
        ],
        asset_formats=[".fbx / .glb (3D)", ".png / .psd (2D/UI)", ".wav / .ogg / .mp3 (Audio)", ".ttf (TMP Fonts)"],
        architecture_notes=[
            "URP Mobile Forward Renderer with baked/minimal real-time shadows for 60 FPS",
            "ScriptableObject architecture for recipes, gate modifiers, level chunks, and economy tuning",
            "CanvasScaler (Scale With Screen Size 1080x1920, Match 0.5) + SafeAreaPanel helper",
            "Object pooling for track segments, ingredients, gates, and particle bursts (zero GC spikes)",
            "Monetization: Google Mobile Ads / AppLovin MAX + Unity IAP",
        ],
    ),
    "phaser": TechStackOption(
        id="phaser",
        name="Web HTML5 (Phaser 4 / Three.js + Capacitor)",
        recommended=False,
        complexity="Low",
        license_cost="100% Free (MIT)",
        best_for="Instant-play web games, playable ads, Poki/CrazyGames, or lightweight Capacitor mobile wraps",
        pros=[
            "Instant browser testing and zero-install playable ad export",
            "TypeScript/JavaScript ecosystem and rapid UI iteration",
        ],
        cons=[
            "Requires Capacitor/WebView wrapper for native App Store/Google Play ads & IAP",
            "Lower raw 3D mobile performance compared to native Godot/Unity",
        ],
        asset_formats=[".glb (Three.js)", ".png / .webp (Sprites/UI)", ".mp3 / .ogg (Audio)", ".woff2 / .ttf"],
        architecture_notes=[
            "Scene flow: PreloadScene -> MenuScene -> GameScene -> UIScene (parallel HUD overlay)",
            "Responsive viewport scaling with safe-area CSS env() insets",
            "Capacitor AdMob & RevenueCat/Purchases plugins for native store shipping",
        ],
    ),
    "flutter": TechStackOption(
        id="flutter",
        name="Flutter (Dart)",
        recommended=True,
        complexity="Low",
        license_cost="100% Free (BSD)",
        best_for="Cross-platform iOS & Android consumer apps, gamified utilities, custom rich UI/animations",
        pros=[
            "Single codebase with pixel-identical custom UI/UX and smooth 60/120 FPS Impeller animations",
            "Fast hot reload and strong Material 3 / Cupertino / Rive / Lottie ecosystem",
            "Mature monetization plugins (RevenueCat, in_app_purchase, google_mobile_ads)",
        ],
        cons=[
            "Slightly larger app size than pure native",
            "Not ideal for complex 3D games (use Godot/Unity for 3D)",
        ],
        asset_formats=[".svg / .png (Icons/UI)", ".riv / .json (Rive/Lottie animations)", ".mp3 / .wav (UI SFX)", ".ttf (Google Fonts)"],
        architecture_notes=[
            "Feature-first folders: lib/features/{onboarding,home,core_flow,paywall,settings}",
            "State & routing: Riverpod (or Bloc) + GoRouter with SafeArea and responsive LayoutBuilder",
            "ThemeData Design Tokens mapped directly to extracted HEX palette (ColorScheme.fromSeed + custom tokens)",
            "Monetization & analytics: RevenueCat SDK for paywalls/trials + PostHog/Firebase Analytics",
        ],
    ),
    "react-native": TechStackOption(
        id="react-native",
        name="React Native + Expo (TypeScript)",
        recommended=False,
        complexity="Low",
        license_cost="100% Free (MIT)",
        best_for="Teams coming from TypeScript/React web stack shipping rapid iOS & Android consumer/SaaS apps",
        pros=[
            "TypeScript + React ecosystem, Expo EAS cloud builds & OTA updates",
            "Strong paywall/subscription libraries (RevenueCat, Superwall, Adapty)",
        ],
        cons=[
            "Complex custom animations require Reanimated/Skia tuning",
            "Native module upgrades occasionally need care",
        ],
        asset_formats=[".svg / .png", ".json (Lottie)", ".mp3 / .wav", ".ttf / .otf"],
        architecture_notes=[
            "Expo Router file-based navigation with bottom tab bar + modal paywall stack",
            "Design tokens in theme/tokens.ts + react-native-safe-area-context",
            "Monetization: Superwall or RevenueCat Paywalls + Expo Notifications for retention loops",
        ],
    ),
    "native": TechStackOption(
        id="native",
        name="Native (SwiftUI for iOS / Kotlin Compose for Android)",
        recommended=False,
        complexity="High",
        license_cost="Free SDKs (Apple/Google developer accounts required)",
        best_for="OS-deep apps (Widgets, HealthKit, Live Activities, StoreKit 2 native polish)",
        pros=[
            "Maximum OS integration, smallest binary size, zero cross-platform abstraction friction",
            "First-day access to StoreKit 2, Widgets, Live Activities, and platform accessibility",
        ],
        cons=[
            "Requires maintaining two separate codebases for iOS and Android",
            "Higher initial build time for solo founders or small teams",
        ],
        asset_formats=["SF Symbols / Material Symbols", ".svg / .pdf / .png", ".wav / .caf"],
        architecture_notes=[
            "MVVM clean architecture with native StoreKit 2 / Google Play Billing Library",
            "Native Home Screen Widgets & Lock Screen Live Activities for D7/D30 retention",
        ],
    ),
}

# Keyword rules that map free-text Turkish/English ideas to clean Mechanic Benchmark Queries vs Domain Topics
_MECHANIC_MAP: list[tuple[tuple[str, ...], str]] = [
    (("kapı", "kapılar", "gate", "math gate", "çarpma", "geçtiğin", "crowd", "stack", "dizilim", "koşu", "runner"), "hypercasual runner stack gate game"),
    (("birleştir", "merge"), "merge puzzle game"),
    (("idle", "tycoon", "fabrika", "işletme", "restoran işlet", "dükkan"), "idle arcade tycoon game"),
    (("match", "eşleştir", "patlat", "puzzle", "bulmaca", "sort", "sıralama"), "casual sort match puzzle game"),
    (("tower defense", "kule savunma"), "tower defense strategy game"),
    (("roguelike", "survivor", "deckbuilder", "kart"), "roguelike survivor mobile game"),
    (("hypercasual", "hyper casual", "hiper casual"), "hypercasual mobile game"),
    (("alışkanlık", "habit", "rutin", "routine"), "habit tracker routine app"),
    (("kalori", "diyet", "beslenme", "calorie", "nutrition", "fasting"), "calorie counter nutrition tracker app"),
    (("bütçe", "finans", "harcama", "budget", "expense"), "personal budget expense tracker app"),
    (("odak", "pomodoro", "yapılacak", "todo", "task", "not"), "focus timer task planner app"),
    (("fitness", "egzersiz", "workout", "spor"), "home workout fitness tracker app"),
    (("dil", "kelime", "language", "flashcard"), "language learning flashcard app"),
]

_DOMAIN_TOPIC_MAP: list[tuple[tuple[str, ...], str, list[str]]] = [
    (
        ("yemek", "hamburger", "burger", "sandviç", "pizza", "mutfak", "aşçı", "cooking", "food", "chef"),
        "burger cooking food",
        [
            "classic hamburger layers assembly order bottom bun to top bun",
            "fast food burger ingredients toppings sauce combinations",
            "cooking game food preparation stages grilling stacking visual cues",
        ],
    ),
    (
        ("kahve", "coffee", "barista", "kafe", "cafe", "içecek"),
        "coffee barista drink",
        [
            "espresso coffee drink recipes layers latte cappuccino mocha",
            "coffee shop toppings syrups cup sizes serving workflow",
        ],
    ),
    (
        ("pasta", "tatlı", "cake", "bakery", "fırın", "donut"),
        "cake bakery dessert",
        [
            "layer cake frosting decorating stages bakery techniques",
            "popular pastry donut toppings glazes flavor combinations",
        ],
    ),
    (
        ("araba", "yarış", "modifiye", "car", "racing", "drift"),
        "car racing vehicle",
        [
            "arcade car tuning upgrades visual progression parts",
            "drift physics visual feedback tire smoke speed cues",
        ],
    ),
    (
        ("alışkanlık", "habit", "rutin", "routine"),
        "habit formation behavioral science",
        [
            "habit loop cue routine reward behavioral psychology James Clear BJ Fogg",
            "streak mechanics habit tracker drop-off recovery psychology",
        ],
    ),
    (
        ("kalori", "diyet", "beslenme", "calorie", "nutrition"),
        "nutrition calorie tracking",
        [
            "macronutrient tracking daily calorie calculation basics TDEE",
            "portion size estimation food logging UX friction reduction",
        ],
    ),
    (
        ("bütçe", "finans", "harcama", "budget", "expense"),
        "personal finance budgeting",
        [
            "50 30 20 budgeting categories zero-based budgeting fundamentals",
            "personal finance expense categorization user habits",
        ],
    ),
]


def recommend_tech_stacks(idea: str, product_mode: str = "auto") -> list[TechStackOption]:
    """Recommend 3 ranked technology stack options with pros, cons, and complexity."""
    mode = detect_product_mode(query=idea, explicit_mode=product_mode)
    low = (idea or "").lower()

    if mode == "game":
        godot = TechStackOption(**TECH_PROFILES["godot"].__dict__)
        unity = TechStackOption(**TECH_PROFILES["unity"].__dict__)
        phaser = TechStackOption(**TECH_PROFILES["phaser"].__dict__)
        if any(k in low for k in ("publisher", "voodoo", "supersonic", "applovin", "unity")):
            unity.recommended = True
            godot.recommended = False
            return [unity, godot, phaser]
        if any(k in low for k in ("web", "browser", "playable", "tarayıcı", "html5")):
            phaser.recommended = True
            godot.recommended = False
            return [phaser, godot, unity]
        godot.recommended = True
        unity.recommended = False
        return [godot, unity, phaser]

    flutter = TechStackOption(**TECH_PROFILES["flutter"].__dict__)
    rn = TechStackOption(**TECH_PROFILES["react-native"].__dict__)
    native = TechStackOption(**TECH_PROFILES["native"].__dict__)
    if any(k in low for k in ("react", "expo", "typescript", "javascript")):
        rn.recommended = True
        flutter.recommended = False
        return [rn, flutter, native]
    if any(k in low for k in ("swiftui", "widget", "healthkit", "live activities", "only ios", "sadece ios")):
        native.recommended = True
        flutter.recommended = False
        return [native, flutter, rn]
    flutter.recommended = True
    rn.recommended = False
    return [flutter, rn, native]


def get_tech_profile(tech_id: str) -> TechStackOption | None:
    """Resolve a normalized tech stack profile by ID or alias."""
    norm = (tech_id or "").strip().lower()
    aliases = {
        "godot4": "godot",
        "godot 4": "godot",
        "unity6": "unity",
        "unity 6": "unity",
        "rn": "react-native",
        "expo": "react-native",
        "react_native": "react-native",
        "swiftui": "native",
        "kotlin": "native",
        "threejs": "phaser",
        "html5": "phaser",
        "web": "phaser",
    }
    key = aliases.get(norm, norm)
    return TECH_PROFILES.get(key)


def decompose_idea(
    idea: str,
    product_mode: str = "auto",
    selected_tech: str = "",
    explicit_mechanic_query: str = "",
    explicit_domain_topics: list[str] | None = None,
    explicit_theme: str = "",
) -> IdeaBrief:
    """Split a raw user idea into (1) mechanic-focused store benchmark query and (2) real-world domain research topics."""
    mode = detect_product_mode(query=idea, explicit_mode=product_mode)
    low = (idea or "").lower()

    # 1. Competitor benchmark query (mechanic/category axis, NOT narrow theme!)
    mechanic_query = (explicit_mechanic_query or "").strip()
    if not mechanic_query:
        for keywords, query_str in _MECHANIC_MAP:
            if any(k in low for k in keywords):
                mechanic_query = query_str
                break
    if not mechanic_query:
        mechanic_query = "hypercasual mobile game" if mode == "game" else idea.strip()[:60]

    # 2. Domain / subject-matter research topics (real-world knowledge axis)
    theme_label = (explicit_theme or "").strip()
    domain_topics = [t.strip() for t in (explicit_domain_topics or []) if t and t.strip()]

    if not domain_topics or not theme_label:
        for keywords, t_label, topics in _DOMAIN_TOPIC_MAP:
            if any(k in low for k in keywords):
                if not theme_label:
                    theme_label = t_label
                if not domain_topics:
                    domain_topics = list(topics)
                break

    if not theme_label:
        theme_label = "stylized arcade game" if mode == "game" else "modern mobile utility app"
    if not domain_topics and idea.strip():
        domain_topics = [
            f"{theme_label} core fundamentals structure elements",
            f"{theme_label} visual hierarchy user expectations best practices",
        ]

    options = recommend_tech_stacks(idea, product_mode=mode)
    resolved_tech = selected_tech.strip().lower()
    if resolved_tech:
        prof = get_tech_profile(resolved_tech)
        if prof:
            resolved_tech = prof.id

    return IdeaBrief(
        raw_idea=idea.strip(),
        product_mode=mode,
        mechanic_query=mechanic_query,
        theme_label=theme_label,
        domain_topics=domain_topics,
        selected_tech=resolved_tech,
        tech_options=options,
    )


def research_domain_knowledge(
    domain_topics: list[str],
    lang: str = "en",
    country: str = "us",
    max_per_topic: int = 3,
    polite_delay_sec: float = 0.5,
) -> list[DomainEvidenceItem]:
    """Run zero-API-key web research on real-world subject matter (e.g. burger layer order, cooking steps)."""
    items: list[DomainEvidenceItem] = []
    seen_urls: set[str] = set()
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    for idx, topic in enumerate(domain_topics):
        clean_topic = (topic or "").strip()
        if not clean_topic:
            continue
        if idx > 0 and polite_delay_sec > 0:
            time.sleep(polite_delay_sec)
        hits = search_duckduckgo_html(clean_topic, max_results=max_per_topic, lang=lang, country=country)
        for hit in hits:
            u = hit["url"]
            if u in seen_urls:
                continue
            seen_urls.add(u)
            items.append(DomainEvidenceItem(
                evidence_id=f"EV-DOM-{len(items) + 1:02d}",
                topic=clean_topic,
                query=clean_topic,
                title=hit["title"],
                url=u,
                domain=hit["domain"],
                snippet=hit["snippet"],
                fetched_at=now_iso,
            ))
    return items
