"""Free UI/UX kit, 3D/2D model pack, SFX/audio kit, font, and engine SDK recommender & web finder."""

from __future__ import annotations

import time
from urllib.parse import urlparse

from .models import AssetKitItem
from .utils import validate_public_web_url
from .web_researcher import search_duckduckgo_html

# Verified, high-quality, permanently free (CC0 / MIT / SIL OFL / Royalty-Free) starter kits
_CURATED_GAME_KITS: list[dict] = [
    # UI/UX Kits
    {
        "category": "ui_ux",
        "name": "Kenney UI Pack & Mobile Controls",
        "source": "Kenney.nl",
        "url": "https://kenney.nl/assets/ui-pack",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".png", ".svg", "9-slice sprites"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "Clean buttons, progress bars, level panels, toggles, and mobile HUD sliders ready for CanvasLayer/uGUI.",
    },
    {
        "category": "ui_ux",
        "name": "Kenney Game Icons & Onscreen Controls",
        "source": "Kenney.nl",
        "url": "https://kenney.nl/assets/game-icons",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".png", ".svg"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "High-contrast icons for audio mute, pause, retry, shop, ads, settings, and coins.",
    },
    {
        "category": "ui_ux",
        "name": "Game-Icons.net (4,000+ Vector Game Icons)",
        "source": "Game-Icons.net",
        "url": "https://game-icons.net/",
        "license": "CC BY 3.0",
        "formats": [".svg", ".png"],
        "tech_fit": ["godot", "unity", "phaser", "flutter"],
        "usage_note": "Customizable color/stroke game icons for abilities, ingredients, power-ups, and achievements.",
    },
    # Fonts
    {
        "category": "fonts",
        "name": "Google Fonts — Fredoka & Outfit (Hypercasual / Casual Pairing)",
        "source": "Google Fonts",
        "url": "https://fonts.google.com/specimen/Fredoka",
        "license": "SIL Open Font License 1.1",
        "formats": [".ttf", ".woff2"],
        "tech_fit": ["godot", "unity", "phaser", "flutter", "react-native"],
        "usage_note": "Rounded bold display font with crisp readability at mobile HUD sizes (scores, gate multipliers +10 / x2).",
    },
    # General 3D/2D Models
    {
        "category": "models_sprites",
        "name": "Kenney Prototype & Stylized 3D Kits",
        "source": "Kenney.nl",
        "url": "https://kenney.nl/assets/category:3D",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".glb", ".fbx", ".obj"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "Modular low-poly 3D kits (direct glTF/GLB drag-and-drop into Godot 4 and Unity) for tracks, props, and gates.",
    },
    {
        "category": "models_sprites",
        "name": "Quaternius Ultimate Stylized 3D Packs",
        "source": "Quaternius",
        "url": "https://quaternius.com/index.html",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".glb", ".fbx", ".obj"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "Game-ready animated characters, stylized environments, and props optimized for 60 FPS mobile rendering.",
    },
    {
        "category": "models_sprites",
        "name": "Poly Pizza Free Low-Poly 3D Library",
        "source": "Poly Pizza",
        "url": "https://poly.pizza/",
        "license": "CC0 / CC-BY (filterable)",
        "formats": [".glb", ".gltf", ".fbx"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "Search thousands of lightweight stylized 3D models by keyword (filter CC0 for attribution-free commercial use).",
    },
    # Audio & SFX
    {
        "category": "audio_sfx",
        "name": "Kenney Interface, Impact & Digital Audio Packs",
        "source": "Kenney.nl",
        "url": "https://kenney.nl/assets/interface-sounds",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".ogg", ".wav"],
        "tech_fit": ["godot", "unity", "phaser", "flutter"],
        "usage_note": "Crisp UI clicks, pop/collect chimes, gate pass whooshes, impact thuds, and reward stingers.",
    },
    {
        "category": "audio_sfx",
        "name": "Freesound.org (CC0 Filtered SFX Library)",
        "source": "Freesound",
        "url": "https://freesound.org/search/?q=game+ui+pop&f=license:%22Creative+Commons+0%22",
        "license": "CC0 1.0",
        "formats": [".wav", ".ogg", ".mp3"],
        "tech_fit": ["godot", "unity", "phaser", "flutter", "react-native"],
        "usage_note": "Theme-specific foley SFX (e.g. sizzling grill, crunchy bite, coin cascade, crowd cheer) with CC0 filter.",
    },
    {
        "category": "audio_sfx",
        "name": "Mixkit Free Game Sound Effects & Music",
        "source": "Mixkit",
        "url": "https://mixkit.co/free-sound-effects/game/",
        "license": "Mixkit Free License (Royalty-Free)",
        "formats": [".wav", ".mp3"],
        "tech_fit": ["godot", "unity", "phaser"],
        "usage_note": "Ready-to-use arcade win fanfares, combo pings, level complete jingles, and upbeat background loops.",
    },
]

_THEME_SPECIFIC_KITS: list[tuple[tuple[str, ...], list[dict]]] = [
    (
        ("food", "burger", "hamburger", "cooking", "yemek", "mutfak", "cafe", "coffee", "cake", "pizza"),
        [
            {
                "category": "models_sprites",
                "name": "Kenney Food Kit (3D Burgers, Buns, Toppings, Kitchen Props)",
                "source": "Kenney.nl",
                "url": "https://kenney.nl/assets/food-kit",
                "license": "CC0 1.0 (Public Domain)",
                "formats": [".glb", ".fbx", ".obj"],
                "tech_fit": ["godot", "unity", "phaser"],
                "usage_note": "Includes modular burger buns, patties, cheese, lettuce, fries, drinks, and serving trays — ideal for gate/stack cooking games.",
            },
            {
                "category": "models_sprites",
                "name": "KayKit Restaurant Bits (Free Edition)",
                "source": "KayKit / itch.io",
                "url": "https://kaylousberg.itch.io/restaurant-bits",
                "license": "CC0 1.0 (Public Domain)",
                "formats": [".glb", ".fbx", ".obj"],
                "tech_fit": ["godot", "unity", "phaser"],
                "usage_note": "Stylized kitchen counters, stoves, plates, utensils, and food props matching vibrant hypercasual art direction.",
            },
            {
                "category": "audio_sfx",
                "name": "Freesound Cooking & Sizzle SFX (CC0)",
                "source": "Freesound",
                "url": "https://freesound.org/search/?q=cooking+sizzle+pop&f=license:%22Creative+Commons+0%22",
                "license": "CC0 1.0",
                "formats": [".wav", ".ogg"],
                "tech_fit": ["godot", "unity", "phaser"],
                "usage_note": "Grill sizzle, chopping, plate clink, and soft squishy ingredient stack sounds for tactile cooking juice.",
            },
        ],
    ),
    (
        ("car", "racing", "vehicle", "araba", "yarış"),
        [
            {
                "category": "models_sprites",
                "name": "Kenney Car Kit & Racing Kit (3D)",
                "source": "Kenney.nl",
                "url": "https://kenney.nl/assets/car-kit",
                "license": "CC0 1.0 (Public Domain)",
                "formats": [".glb", ".fbx", ".obj"],
                "tech_fit": ["godot", "unity", "phaser"],
                "usage_note": "Low-poly stylized vehicles, ramps, barriers, and track tiles ready for mobile 60 FPS.",
            },
        ],
    ),
]

_CURATED_APP_KITS: list[dict] = [
    {
        "category": "ui_ux",
        "name": "Material 3 Design Kit (Figma Community Official)",
        "source": "Figma Community",
        "url": "https://www.figma.com/community/file/1035203688168086460",
        "license": "CC BY 4.0 / Free",
        "formats": ["Figma", "Design Tokens"],
        "tech_fit": ["flutter", "react-native", "native"],
        "usage_note": "Complete mobile navigation bars, bottom sheets, cards, chips, and dynamic color token templates.",
    },
    {
        "category": "ui_ux",
        "name": "Apple iOS Design Resources (Figma Official)",
        "source": "Figma Community / Apple",
        "url": "https://www.figma.com/community/file/1248375255495415511",
        "license": "Free (Apple Design License)",
        "formats": ["Figma", "iOS Components"],
        "tech_fit": ["flutter", "react-native", "native"],
        "usage_note": "Authentic iOS safe-area templates, tab bars, paywall sheets, and native system modals.",
    },
    {
        "category": "ui_ux",
        "name": "Lucide & Phosphor Open-Source Icon Kits",
        "source": "Lucide / Phosphor",
        "url": "https://lucide.dev/",
        "license": "ISC / MIT (Free)",
        "formats": [".svg", "Flutter/React packages"],
        "tech_fit": ["flutter", "react-native", "native", "phaser"],
        "usage_note": "1,500+ crisp stroke-consistent icons for tab bars, onboarding checklists, and paywall feature lists.",
    },
    {
        "category": "models_sprites",
        "name": "LottieFiles & unDraw Free Vector Illustrations / Micro-Animations",
        "source": "unDraw / LottieFiles",
        "url": "https://undraw.co/illustrations",
        "license": "Open Source / Free",
        "formats": [".svg", ".json (Lottie)"],
        "tech_fit": ["flutter", "react-native", "native"],
        "usage_note": "Customizable-color onboarding illustrations, empty-state visuals, and success celebrations.",
    },
    {
        "category": "fonts",
        "name": "Google Fonts — Plus Jakarta Sans & Inter",
        "source": "Google Fonts",
        "url": "https://fonts.google.com/specimen/Plus+Jakarta+Sans",
        "license": "SIL Open Font License 1.1",
        "formats": [".ttf", ".woff2"],
        "tech_fit": ["flutter", "react-native", "native", "godot", "unity"],
        "usage_note": "High-legibility geometric mobile UI typeface with tabular numerals for metrics and pricing cards.",
    },
    {
        "category": "audio_sfx",
        "name": "Kenney Interface Sounds (Subtle Mobile UI Feedback)",
        "source": "Kenney.nl",
        "url": "https://kenney.nl/assets/interface-sounds",
        "license": "CC0 1.0 (Public Domain)",
        "formats": [".ogg", ".wav"],
        "tech_fit": ["flutter", "react-native", "native"],
        "usage_note": "Soft micro-interaction ticks, task-complete chimes, and streak-celebration audio cues.",
    },
]

_TECH_SDK_KITS: dict[str, list[dict]] = {
    "godot": [
        {
            "category": "engine_sdk",
            "name": "Poing Studios Godot AdMob Plugin (Godot 4)",
            "source": "GitHub / Godot Asset Library",
            "url": "https://github.com/poing-studios/godot-admob-plugin",
            "license": "MIT (Free)",
            "formats": ["Godot 4 Addon"],
            "tech_fit": ["godot"],
            "usage_note": "Banner, Interstitial, Rewarded, and App Open ads integration for Android & iOS in Godot 4.",
        },
        {
            "category": "engine_sdk",
            "name": "Godot Shaders Library (Free 2D/3D Mobile Shaders)",
            "source": "GodotShaders.com",
            "url": "https://godotshaders.com/",
            "license": "CC0 / MIT (per shader)",
            "formats": [".gdshader"],
            "tech_fit": ["godot"],
            "usage_note": "Toon outlines, glossy food highlights, gate glow portals, hit flashes, and stylized water shaders.",
        },
        {
            "category": "engine_sdk",
            "name": "Phantom Camera for Godot 4",
            "source": "GitHub / Godot Asset Library",
            "url": "https://github.com/ramokz/phantom-camera",
            "license": "MIT (Free)",
            "formats": ["Godot 4 Addon"],
            "tech_fit": ["godot"],
            "usage_note": "Smooth follow camera, look-ahead, dynamic FOV zoom, and finish-line camera transitions.",
        },
    ],
    "unity": [
        {
            "category": "engine_sdk",
            "name": "DOTween (HOTween v2) Free Edition",
            "source": "Demigiant / Unity Asset Store",
            "url": "https://dotween.demigiant.com/",
            "license": "Free Standard License",
            "formats": ["Unity Package"],
            "tech_fit": ["unity"],
            "usage_note": "Industry-standard tweening for hypercasual juice: punch scale, stack bounce, UI pops, and camera shake.",
        },
        {
            "category": "engine_sdk",
            "name": "Google Mobile Ads Unity Plugin",
            "source": "GitHub / Google",
            "url": "https://github.com/googleads/googleads-mobile-unity",
            "license": "Apache 2.0 (Free)",
            "formats": [".unitypackage"],
            "tech_fit": ["unity"],
            "usage_note": "Official Banner, Interstitial, and Rewarded ad integration for Unity mobile builds.",
        },
    ],
    "flutter": [
        {
            "category": "engine_sdk",
            "name": "RevenueCat Purchases Flutter SDK (Free Starter Tier)",
            "source": "pub.dev / RevenueCat",
            "url": "https://pub.dev/packages/purchases_flutter",
            "license": "MIT SDK / Free up to $2.5K MTR",
            "formats": ["Dart Package"],
            "tech_fit": ["flutter"],
            "usage_note": "Cross-platform iOS/Android subscriptions, trials, paywall A/B testing, and receipt validation.",
        },
        {
            "category": "engine_sdk",
            "name": "Rive Flutter Runtime (Interactive Vector Animations)",
            "source": "pub.dev / Rive",
            "url": "https://pub.dev/packages/rive",
            "license": "MIT (Free)",
            "formats": ["Dart Package", ".riv"],
            "tech_fit": ["flutter"],
            "usage_note": "State-machine driven onboarding illustrations, streak flames, and celebratory animations.",
        },
    ],
    "react-native": [
        {
            "category": "engine_sdk",
            "name": "Expo + React Native Purchases (RevenueCat)",
            "source": "npm / RevenueCat",
            "url": "https://www.revenuecat.com/docs/getting-started/installation/reactnative",
            "license": "MIT SDK / Free Starter Tier",
            "formats": ["npm Package"],
            "tech_fit": ["react-native"],
            "usage_note": "Plug-and-play subscriptions, free trials, and remote paywall configuration for Expo/RN apps.",
        },
    ],
    "phaser": [
        {
            "category": "engine_sdk",
            "name": "Capacitor Community AdMob & Purchases",
            "source": "GitHub / Capacitor Community",
            "url": "https://github.com/capacitor-community/admob",
            "license": "MIT (Free)",
            "formats": ["npm Package"],
            "tech_fit": ["phaser"],
            "usage_note": "Bridge HTML5/Phaser/Three.js games to native iOS & Android AdMob placements.",
        },
    ],
}


def find_free_asset_kits(
    product_mode: str = "game",
    selected_tech: str = "godot",
    theme_label: str = "",
    run_live_web_search: bool = True,
    lang: str = "en",
    country: str = "us",
) -> list[AssetKitItem]:
    """Assemble verified free UI/UX, 3D/2D model, audio/SFX, font, and SDK kits tailored to theme + tech stack."""
    tech = (selected_tech or ("godot" if product_mode == "game" else "flutter")).strip().lower()
    theme_low = (theme_label or "").lower()

    raw_items: list[dict] = []
    if product_mode == "game":
        # Prioritize theme-specific packs first so the most relevant models/SFX lead the catalog
        for keywords, extra_list in _THEME_SPECIFIC_KITS:
            if any(k in theme_low for k in keywords):
                raw_items.extend(extra_list)
        if tech in _TECH_SDK_KITS:
            raw_items.extend(_TECH_SDK_KITS[tech])
        raw_items.extend(_CURATED_GAME_KITS)
    else:
        if tech in _TECH_SDK_KITS:
            raw_items.extend(_TECH_SDK_KITS[tech])
        raw_items.extend(_CURATED_APP_KITS)

    kits: list[AssetKitItem] = []
    seen_urls: set[str] = set()

    for entry in raw_items:
        u = entry["url"]
        if u in seen_urls:
            continue
        seen_urls.add(u)
        kits.append(AssetKitItem(
            evidence_id=f"EV-KIT-{len(kits) + 1:02d}",
            category=entry["category"],
            name=entry["name"],
            source=entry["source"],
            url=u,
            license=entry["license"],
            formats=list(entry.get("formats") or []),
            tech_fit=list(entry.get("tech_fit") or []),
            usage_note=entry.get("usage_note", ""),
            discovery_origin="curated",
        ))

    # Optional live DuckDuckGo enrichment for theme-specific free models, UI kits, and SFX
    if run_live_web_search and theme_label.strip():
        live_queries: list[tuple[str, str]] = (
            [
                ("models_sprites", f'free "{theme_label}" 3D model OR sprite pack CC0 site:itch.io OR site:kenney.nl OR site:opengameart.org'),
                ("ui_ux", f'free mobile game UI kit "{tech}" OR figma CC0 OR MIT'),
                ("audio_sfx", f'free "{theme_label}" sound effects pack CC0 site:itch.io OR site:opengameart.org OR site:freesound.org'),
            ]
            if product_mode == "game"
            else [
                ("ui_ux", f'free "{theme_label}" mobile app UI kit site:figma.com/community'),
                ("models_sprites", f'free "{theme_label}" icon OR illustration pack MIT OR CC0'),
            ]
        )
        for idx, (cat, q) in enumerate(live_queries):
            if idx > 0:
                time.sleep(0.45)
            hits = search_duckduckgo_html(q, max_results=2, lang=lang, country=country)
            for hit in hits:
                u = hit["url"]
                if u in seen_urls:
                    continue
                try:
                    safe_u = validate_public_web_url(u)
                except ValueError:
                    continue
                seen_urls.add(safe_u)
                domain = (urlparse(safe_u).hostname or "").lower()
                kits.append(AssetKitItem(
                    evidence_id=f"EV-KIT-{len(kits) + 1:02d}",
                    category=cat,
                    name=hit["title"][:120] or domain,
                    source=domain,
                    url=safe_u,
                    license="Verify license on page (Free search hit)",
                    formats=[],
                    tech_fit=[tech] if tech else [],
                    usage_note=hit["snippet"][:260],
                    discovery_origin="web_search",
                ))
    return kits
