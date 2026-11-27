"""Idea intake, mechanic-vs-theme decomposition, tech stack advisor, real-world subject profiling, and domain research."""

from __future__ import annotations

import re

from .analyzer import detect_product_mode
from .domain_researcher import research_domain_knowledge_structured
from .models import DomainEvidenceItem, IdeaBrief, TechStackOption

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

# Keyword rules that map free-text Turkish/English ideas to clean Mechanic Benchmark Queries
_MECHANIC_MAP: list[tuple[tuple[str, ...], str]] = [
    (("kapı", "kapılar", "gate", "math gate", "çarpma", "geçtiğin", "crowd", "stack", "dizilim", "koşu", "runner"), "hypercasual runner stack gate game"),
    (("birleştir", "merge"), "merge puzzle game"),
    (("idle", "tycoon", "fabrika", "işletme", "restoran işlet", "dükkan", "butik"), "idle arcade tycoon game"),
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

# Rich real-world subject profiles covering definition, how it is made, layers/anatomy, famous brands, and image queries
_DOMAIN_PROFILES: list[dict] = [
    {
        "keywords": ("hamburger", "burger", "cheeseburger", "fast food", "sandviç", "yemek", "mutfak", "aşçı", "cooking", "food", "chef"),
        "theme_label": "burger cooking food",
        "core_subject": "hamburger",
        "famous_brands": [
            "McDonald's Big Mac",
            "Burger King Whopper",
            "Shake Shack ShackBurger",
            "Five Guys Cheeseburger",
            "In-N-Out Double-Double",
        ],
        "domain_topics": [
            "what is a hamburger real world definition origin anatomy",
            "how a hamburger is made grilling searing assembly stages step by step",
            "classic hamburger layers assembly order bottom bun to top bun ingredients",
            "McDonald's Big Mac vs Burger King Whopper vs Shake Shack burger layers comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Hamburger Katman Anatomisi", "query": "hamburger layers diagram exploded anatomy cross section", "count": 2},
            {"category": "how_its_made", "label": "Izgara ve Hazırlama Süreci", "query": "grilling burger patty melting cheese flat top grill cooking stages", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Gourmet Burger", "query": "classic cheeseburger brioche bun cross section close up food photography", "count": 2},
        ],
    },
    {
        "keywords": ("pizza", "pizzeria", "hamur", "pizzacı"),
        "theme_label": "pizza cooking food",
        "core_subject": "pizza",
        "famous_brands": [
            "Neapolitan Margherita Pizza",
            "Domino's Pepperoni Pizza",
            "Pizza Hut Pan Pizza",
            "New York Style Pizza Slice",
        ],
        "domain_topics": [
            "what is pizza real world styles Neapolitan New York Detroit definition",
            "how pizza is made dough fermentation stretching baking wood fired oven stages",
            "classic pizza layers order dough tomato sauce mozzarella toppings basil",
            "Domino's vs Pizza Hut vs authentic Neapolitan pizza crust toppings comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Pizza Katman Anatomisi", "query": "pizza layers anatomy crust sauce cheese toppings cross section", "count": 2},
            {"category": "how_its_made", "label": "Hamur ve Fırın Süreci", "query": "stretching pizza dough baking brick oven stage process", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek İtalyan Pizza", "query": "authentic neapolitan margherita pizza fresh baked close up", "count": 2},
        ],
    },
    {
        "keywords": ("sushi", "suşi", "ramen", "noodle", "japon", "asian food"),
        "theme_label": "sushi japanese cooking food",
        "core_subject": "sushi",
        "famous_brands": [
            "Nobu Sushi",
            "Kura Revolving Sushi",
            "Sukiyabashi Jiro Nigiri",
            "Ichiran Ramen",
        ],
        "domain_topics": [
            "what is sushi nigiri maki sashimi real world definition Japanese cuisine",
            "how sushi is made vinegared rice rolling slicing preparation steps",
            "sushi roll layers nori shari rice fish fillings toppings order",
            "famous sushi styles Nobu Kura Sushi conveyor belt dining real world experience",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Sushi Katman ve Kesit", "query": "sushi maki roll cross section layers nori rice salmon diagram", "count": 2},
            {"category": "how_its_made", "label": "Sushi Hazırlama Süreci", "query": "sushi chef rolling maki bamboo mat preparation steps", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Sushi Tabağı", "query": "authentic japanese nigiri sushi maki platter photography", "count": 2},
        ],
    },
    {
        "keywords": ("parfüm", "parfume", "perfume", "fragrance", "koku", "esans", "parfumeri"),
        "theme_label": "luxury perfume bottle boutique",
        "core_subject": "perfume",
        "famous_brands": [
            "Chanel No 5",
            "Dior Sauvage",
            "Creed Aventus",
            "Jo Malone London",
            "Maison Francis Kurkdjian Baccarat Rouge 540",
        ],
        "domain_topics": [
            "what is perfume fragrance concentration EdC EdT EdP Extrait real world definition",
            "how luxury perfume is made extraction blending maceration bottling process",
            "perfume fragrance pyramid top heart base notes raw ingredients anatomy",
            "Chanel No 5 Dior Creed Jo Malone luxury perfume bottle design flagship boutique",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Koku Piramidi ve Şişe Anatomisi", "query": "perfume fragrance pyramid top middle base notes diagram", "count": 2},
            {"category": "how_its_made", "label": "Parfüm Üretim ve Laboratuvar", "query": "perfumer organ fragrance laboratory glass bottles blending process", "count": 2},
            {"category": "real_world_equivalent", "label": "Lüks Parfüm Butiği", "query": "luxury perfume flagship boutique Paris interior shelves bottles", "count": 2},
        ],
    },
    {
        "keywords": ("kahve", "coffee", "barista", "kafe", "cafe", "latte", "espresso", "içecek"),
        "theme_label": "coffee barista drink",
        "core_subject": "espresso coffee",
        "famous_brands": [
            "Starbucks Caramel Macchiato",
            "Blue Bottle Coffee Latte",
            "Dunkin Iced Coffee",
            "Illy Espresso",
        ],
        "domain_topics": [
            "what is espresso latte cappuccino flat white coffee drink differences",
            "how specialty coffee is made grinding tamping extraction milk steaming steps",
            "espresso coffee drink layers crema espresso steamed milk microfoam toppings",
            "Starbucks vs Blue Bottle vs specialty cafe menu cups visual branding",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Kahve İçecek Katmanları", "query": "coffee drinks layers diagram espresso latte cappuccino macchiato", "count": 2},
            {"category": "how_its_made", "label": "Barista Demleme Süreci", "query": "barista pulling espresso shot pouring latte art coffee machine", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Kafe Sunumu", "query": "specialty iced latte layered espresso milk glass cafe photo", "count": 2},
        ],
    },
    {
        "keywords": ("pasta", "tatlı", "cake", "bakery", "fırın", "donut", "dondurma", "ice cream", "pastane"),
        "theme_label": "cake bakery dessert",
        "core_subject": "layer cake",
        "famous_brands": [
            "Krispy Kreme Original Glazed Donut",
            "Ladurée Macarons",
            "Magnolia Bakery Cupcake",
            "Crumbl Cookies",
        ],
        "domain_topics": [
            "what is a layer cake pastry bakery dessert real world definition",
            "how a layered cake is made baking crumb coat frosting piping decorating stages",
            "layer cake anatomy sponge filling buttercream glaze toppings cross section",
            "Krispy Kreme Laduree Magnolia Bakery iconic dessert presentation styles",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Pasta Katman Kesiti", "query": "layered cake cross section slice sponge frosting filling photo", "count": 2},
            {"category": "how_its_made", "label": "Pasta Süsleme Süreci", "query": "cake decorating frosting piping turntable bakery process", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Pastane Vitrini", "query": "artisan bakery pastry display showcase cakes donuts", "count": 2},
        ],
    },
    {
        "keywords": ("araba", "yarış", "modifiye", "car", "racing", "drift", "otomobil"),
        "theme_label": "car racing vehicle",
        "core_subject": "sports car",
        "famous_brands": [
            "Porsche 911 GT3",
            "Ferrari F40",
            "Nissan GT-R",
            "Lamborghini Huracan",
        ],
        "domain_topics": [
            "what is a sports car drift racing car aerodynamics real world overview",
            "how car tuning modification works engine turbo suspension bodykit stages",
            "race car visual components spoiler rims exhaust livery brake calipers",
            "Porsche 911 Ferrari Nissan GTR iconic sports car silhouettes comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Otomobil Parça Anatomisi", "query": "sports car exterior parts aerodynamics diagram spoiler diffuser", "count": 2},
            {"category": "how_its_made", "label": "Modifiye ve Garaj Süreci", "query": "car tuning garage mechanic customizing sports car workshop", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Yarış ve Drift", "query": "sports car drifting track tire smoke photography", "count": 2},
        ],
    },
    {
        "keywords": ("moda", "fashion", "kıyafet", "ayakkabı", "sneaker", "giyim"),
        "theme_label": "fashion sneaker boutique",
        "core_subject": "sneaker",
        "famous_brands": [
            "Nike Air Jordan 1",
            "Adidas Superstar",
            "New Balance 550",
            "Converse Chuck Taylor",
        ],
        "domain_topics": [
            "what is sneaker culture streetwear fashion design real world overview",
            "how sneakers are made sole upper stitching assembly manufacturing process",
            "sneaker anatomy outsole midsole toe box tongue heel counter parts",
            "Nike Air Jordan Adidas New Balance iconic sneaker silhouette comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Sneaker Parça Anatomisi", "query": "sneaker anatomy diagram outsole midsole upper toe box parts", "count": 2},
            {"category": "how_its_made", "label": "Ayakkabı Üretim Süreci", "query": "custom sneaker making workshop leather stitching sole assembly", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Sneaker Mağazası", "query": "sneaker boutique display wall streetwear store", "count": 2},
        ],
    },
    {
        "keywords": ("otel", "hotel", "tatil", "resort", "emlak", "dekorasyon", "interior"),
        "theme_label": "hotel resort interior design",
        "core_subject": "luxury hotel",
        "famous_brands": [
            "Ritz-Carlton Hotel",
            "Four Seasons Resort",
            "Hilton Hotel Lobby",
            "Aman Resorts",
        ],
        "domain_topics": [
            "what is luxury hospitality hotel star rating real world guest experience",
            "how a hotel operates check-in housekeeping room service concierge workflow",
            "hotel layout zones lobby reception suite pool spa restaurant anatomy",
            "Ritz-Carlton Four Seasons Aman luxury hotel design cues comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Otel Kat Planı ve Bölgeler", "query": "hotel floor plan lobby guest room layout architecture diagram", "count": 2},
            {"category": "how_its_made", "label": "Otel Operasyon Akışı", "query": "luxury hotel reception check in desk hospitality service", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Lüks Otel", "query": "luxury resort hotel lobby interior architecture photo", "count": 2},
        ],
    },
    {
        "keywords": ("alışkanlık", "habit", "rutin", "routine"),
        "theme_label": "habit formation behavioral science",
        "core_subject": "habit formation",
        "famous_brands": [
            "Atomic Habits Habit Loop",
            "Bullet Journal Habit Tracker",
            "Seinfeld Don't Break the Chain Calendar",
        ],
        "domain_topics": [
            "what is habit formation behavioral psychology real world cue craving response reward",
            "how habits are built step by step BJ Fogg tiny habits James Clear habit stacking",
            "habit loop components trigger routine reward streak recovery mechanics",
            "real world habit tracking methods bullet journal wall calendar Seinfeld chain",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Alışkanlık Döngüsü Anatomisi", "query": "habit loop cue craving response reward diagram psychology", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Hayat Alışkanlık Takibi", "query": "bullet journal paper habit tracker spread notebook desk", "count": 2},
        ],
    },
    {
        "keywords": ("kalori", "diyet", "beslenme", "calorie", "nutrition", "fasting"),
        "theme_label": "nutrition calorie tracking",
        "core_subject": "human nutrition",
        "famous_brands": [
            "Harvard Healthy Eating Plate",
            "FDA Nutrition Facts Label",
            "Mediterranean Diet Pyramid",
        ],
        "domain_topics": [
            "what is macronutrient calorie balance TDEE real world nutrition fundamentals",
            "how daily food logging portion size estimation works step by step",
            "balanced meal plate components protein carbs healthy fats fiber proportions",
            "Harvard Healthy Eating Plate nutrition facts label real world food guides",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Dengeli Tabak ve Makrolar", "query": "balanced meal plate macronutrients protein carbs vegetables diagram", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Öğün Hazırlığı", "query": "healthy meal prep containers portion control food photography", "count": 2},
        ],
    },
    {
        "keywords": ("bütçe", "finans", "harcama", "budget", "expense"),
        "theme_label": "personal finance budgeting",
        "core_subject": "personal budget",
        "famous_brands": [
            "50 30 20 Budget Rule",
            "Cash Envelope Budgeting System",
            "Kakeibo Japanese Budgeting Ledger",
        ],
        "domain_topics": [
            "what is personal budgeting 50 30 20 rule zero-based budgeting real world overview",
            "how monthly expense tracking and budget categorization works step by step",
            "personal budget categories fixed needs wants savings debt structure",
            "real world budgeting methods cash envelopes kakeibo notebook system",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Bütçe Dağılım Modeli", "query": "50 30 20 budget rule pie chart diagram personal finance", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Hayat Bütçe Defteri", "query": "cash envelope budgeting planner notebook real life", "count": 2},
        ],
    },
    {
        "keywords": ("fitness", "egzersiz", "workout", "spor"),
        "theme_label": "fitness workout training",
        "core_subject": "strength training",
        "famous_brands": [
            "Nike Training Club",
            "Peloton Workout Studio",
            "CrossFit Gym Workout",
        ],
        "domain_topics": [
            "what is strength and bodyweight training progressive overload real world basics",
            "how a structured workout session works warmup sets rest cooldown stages",
            "muscle group training split push pull legs core anatomy",
            "real world gym and home workout equipment routines comparison",
        ],
        "base_image_queries": [
            {"category": "anatomy_layers", "label": "Kas Grupları Anatomisi", "query": "human muscle groups workout anatomy chart diagram", "count": 2},
            {"category": "real_world_equivalent", "label": "Gerçek Egzersiz Ortamı", "query": "home workout dumbbells exercise mat training photo", "count": 2},
        ],
    },
]

# Generic game/app filler words stripped when dynamically inferring core_subject for unseen ideas
_SUBJECT_STOPWORDS: frozenset[str] = frozenset({
    "oyun", "oyunu", "oyunlari", "oyunları", "uygulama", "uygulamasi", "uygulaması",
    "mobil", "mobile", "game", "games", "app", "apps", "istiyorum", "yapmak", "yapma",
    "tasarlamak", "want", "build", "make", "create", "design", "hypercasual", "casual",
    "hybridcasual", "tycoon", "idle", "runner", "stack", "gate", "kapi", "kapı",
    "kapilar", "kapılar", "kapilardan", "kapılardan", "gectigin", "geçtiğin", "dizilim",
    "dizilimi", "simulator", "simülatör", "puzzle", "merge", "arcade", "ios", "android",
    "2d", "3d", "godot", "unity", "flutter", "react", "native", "phaser", "bir", "ve",
    "ile", "icin", "için", "gibi", "olan", "the", "and", "with", "where", "players",
    "player", "users", "user", "for", "from", "into", "that", "this", "using", "about",
    "my", "own", "new", "best", "top", "super", "pro",
})


def extract_core_subject(idea: str, fallback: str = "") -> str:
    """Dynamically extract the concrete real-world subject from any free-text TR/EN idea."""
    raw = (idea or "").strip()
    if not raw:
        return fallback.strip()
    tokens = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9'-]+", raw)
    kept: list[str] = []
    for tok in tokens:
        low = tok.lower().strip("'-")
        if len(low) < 2 or low in _SUBJECT_STOPWORDS or low.isdigit():
            continue
        if low not in {k.lower() for k in kept}:
            kept.append(tok)
        if len(kept) >= 3:
            break
    if kept:
        return " ".join(kept)
    return fallback.strip() or raw[:40]


def build_domain_image_queries(
    core_subject: str,
    famous_brands: list[str] | None = None,
    base_queries: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Build balanced real-world visual reference image queries (anatomy, process, real life, and famous brands)."""
    subj = (core_subject or "").strip()
    queries: list[dict[str, str]] = []
    seen_q: set[str] = set()

    def _add(category: str, label: str, query: str, count: int = 1) -> None:
        clean_q = (query or "").strip()
        if not clean_q or clean_q.lower() in seen_q:
            return
        seen_q.add(clean_q.lower())
        queries.append({
            "category": category,
            "label": label.strip() or clean_q[:40],
            "query": clean_q,
            "count": str(max(1, count)),
        })

    if base_queries:
        for bq in base_queries:
            _add(
                bq.get("category", "real_world_equivalent"),
                bq.get("label", subj),
                bq.get("query", ""),
                int(bq.get("count", 1)),
            )
    elif subj:
        _add("anatomy_layers", f"{subj.title()} Anatomi / Katmanlar", f"{subj} layers parts anatomy diagram cross section", 2)
        _add("how_its_made", f"{subj.title()} Hazırlama Süreci", f"how {subj} is made step by step preparation process photo", 2)
        _add("real_world_equivalent", f"Gerçek Hayat {subj.title()}", f"real life {subj} close up high quality photography", 2)

    brands = [b.strip() for b in (famous_brands or []) if b and b.strip()]
    if brands:
        for brand in brands[:5]:
            brand_q = brand if subj and subj.lower() in brand.lower() else f"{brand} {subj}".strip()
            _add("famous_brand", brand, f"{brand_q} product photo", 1)
    elif subj:
        _add("famous_brand", f"Ünlü {subj.title()} Markaları", f"most famous iconic {subj} brands real product photo", 2)

    return queries


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
    explicit_subject: str = "",
    explicit_famous_brands: list[str] | None = None,
) -> IdeaBrief:
    """Split a raw user idea into (1) mechanic-focused store benchmark query and (2) structured real-world subject + famous brand research."""
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

    # 2. Real-world subject, famous brands, domain topics, and visual reference queries
    theme_label = (explicit_theme or "").strip()
    core_subject = (explicit_subject or "").strip()
    famous_brands = [b.strip() for b in (explicit_famous_brands or []) if b and b.strip()]
    domain_topics = [t.strip() for t in (explicit_domain_topics or []) if t and t.strip()]
    matched_profile: dict | None = None

    search_blob = f"{idea} {explicit_subject} {explicit_theme}".lower()
    for profile in _DOMAIN_PROFILES:
        if any(k in search_blob for k in profile["keywords"]):
            matched_profile = profile
            break

    if matched_profile:
        if not theme_label:
            theme_label = matched_profile["theme_label"]
        if not core_subject:
            core_subject = matched_profile["core_subject"]
        if not famous_brands:
            famous_brands = list(matched_profile["famous_brands"])
        if not domain_topics:
            domain_topics = list(matched_profile["domain_topics"])

    # Dynamic subject extraction for any custom idea not covered by built-in profiles
    if not core_subject:
        core_subject = extract_core_subject(idea or theme_label, fallback=theme_label or ("mobile game" if mode == "game" else "mobile app"))
    if not theme_label:
        theme_label = core_subject if core_subject else ("stylized arcade game" if mode == "game" else "modern mobile utility app")

    if not domain_topics and core_subject:
        domain_topics = [
            f"what is {core_subject} real world definition equivalent overview",
            f"how {core_subject} is made step by step preparation process stages",
            f"{core_subject} layers anatomy components parts order structure",
            f"most famous {core_subject} brands iconic real world examples comparison",
        ]

    base_img_queries = (
        matched_profile["base_image_queries"]
        if matched_profile and (not explicit_subject or explicit_subject.strip().lower() == matched_profile["core_subject"].lower())
        else None
    )
    image_queries = build_domain_image_queries(
        core_subject=core_subject,
        famous_brands=famous_brands,
        base_queries=base_img_queries,
    )

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
        core_subject=core_subject,
        famous_brands=famous_brands,
        domain_topics=domain_topics,
        image_queries=image_queries,
        selected_tech=resolved_tech,
        tech_options=options,
    )


def research_domain_knowledge(
    domain_topics: list[str],
    lang: str = "en",
    country: str = "us",
    max_per_topic: int = 3,
    polite_delay_sec: float = 0.35,
    core_subject: str = "",
    famous_brands: list[str] | None = None,
) -> list[DomainEvidenceItem]:
    """Run zero-API-key real-world subject & famous brand knowledge research (Wikipedia API + DuckDuckGo)."""
    return research_domain_knowledge_structured(
        domain_topics=domain_topics,
        core_subject=core_subject,
        famous_brands=famous_brands,
        lang=lang,
        country=country,
        max_per_topic=max_per_topic,
        polite_delay_sec=polite_delay_sec,
    )
