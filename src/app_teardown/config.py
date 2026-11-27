"""Central configuration, security allowlists, and domain signal vocabularies."""

from __future__ import annotations

from pathlib import Path

PACKAGE_VERSION = "1.1.0"

DEFAULT_RESEARCH_DIR = Path.cwd() / "teardowns"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT_SEC = 20
DOWNLOAD_TIMEOUT_SEC = 30
VIDEO_TIMEOUT_SEC = 180
MAX_DOWNLOAD_WORKERS = 6

MAX_IMAGE_BYTES = 20 * 1024 * 1024       # 20 MB per image
MAX_VIDEO_BYTES = 180 * 1024 * 1024      # 180 MB cap per gameplay video
DEFAULT_MAX_VIDEO_SEC = 240              # First 4 minutes (FTUE + core loop + early monetization)
DEFAULT_MAX_FRAMES = 24                  # Hybrid scene-change + interval frames per video
DEFAULT_SCENE_THRESHOLD = 0.28           # FFmpeg scene detection delta threshold
DEFAULT_MIN_FRAME_GAP_SEC = 3.5          # Minimum spacing between extracted frames

# Strict CDN/store allowlist for binary asset & store API downloads (SSRF defense)
ALLOWED_ASSET_HOST_SUFFIXES: tuple[str, ...] = (
    "apple.com",
    "mzstatic.com",
    "itunes.apple.com",
    "apps.apple.com",
    "rss.applemarketingtools.com",
    "play.google.com",
    "googleusercontent.com",
    "ggpht.com",
    "gstatic.com",
    "youtube.com",
    "youtu.be",
    "ytimg.com",
    "googlevideo.com",
    "duckduckgo.com",
)

# Categories and terms used to auto-detect game vs non-game app mode
GAME_CATEGORY_HINTS: frozenset[str] = frozenset({
    "game", "games", "action", "adventure", "arcade", "board", "card", "casino",
    "casual", "hypercasual", "puzzle", "racing", "role playing", "rpg",
    "simulation", "strategy", "trivia", "word", "sports", "shooter", "roguelike",
    "idle", "merge", "tower defense", "platformer", "sandbox", "match-3",
})

GAME_QUERY_HINTS: frozenset[str] = frozenset({
    "game", "games", "oyun", "hypercasual", "casual", "hybridcasual", "puzzle",
    "merge", "idle", "tycoon", "roguelike", "deckbuilder", "shooter", "fps",
    "rpg", "mmorpg", "moba", "arcade", "runner", "platformer", "tower defense",
    "match 3", "match-3", "card game", "survivor", "simulator", "racing", "gacha",
})

# Automated signal lexicons for monetization, ads, retention, and review sentiment
AD_FORMAT_PATTERNS: dict[str, tuple[str, ...]] = {
    "rewarded_video": (
        "watch ad", "watch an ad", "watch video", "rewarded", "extra life",
        "double reward", "2x reward", "free revive", "reklam izle", "ödüllü reklam",
    ),
    "interstitial": (
        "after every level", "every level", "between levels", "forced ad",
        "unskippable", "pop up ad", "popup ad", "30 second ad", "ad every",
        "her bölüm", "zorunlu reklam", "geçilemeyen reklam",
    ),
    "banner": (
        "banner ad", "bottom ad", "ad at the bottom", "banner reklam",
    ),
    "no_ads_iap": (
        "remove ads", "no ads", "ad-free", "ad free", "reklamları kaldır", "reklamsız",
    ),
}

RETENTION_HOOK_PATTERNS: dict[str, tuple[str, ...]] = {
    "daily_rewards_streak": (
        "daily reward", "daily bonus", "daily login", "streak", "check-in",
        "günlük ödül", "seri", "streak freeze",
    ),
    "missions_quests": (
        "daily quest", "mission", "challenge", "achievement", "milestone",
        "görev", "başarım",
    ),
    "battle_pass_seasons": (
        "battle pass", "season pass", "vip pass", "seasonal event", "season",
        "sezon bileti", "vip",
    ),
    "meta_progression": (
        "upgrade", "unlock", "collect", "customize", "build your", "decorate",
        "level up", "skill tree", "talent", "yükselt", "kilidini aç",
    ),
    "social_competitive": (
        "leaderboard", "clan", "guild", "multiplayer", "pvp", "tournament",
        "friends", "co-op", "sıralama", "turnuva",
    ),
    "live_ops_events": (
        "limited time", "special event", "weekly event", "new event", "live event",
        "sınırlı süreli", "etkinlik",
    ),
    "habit_personalization": (
        "reminder", "notification", "personalized", "ai coach", "insights",
        "weekly report", "widget", "hatırlatıcı", "kişiselleştirilmiş",
    ),
    "offline_play": (
        "offline", "no wifi", "no internet", "çevrimdışı", "internetsiz",
    ),
}

REVIEW_FRICTION_PATTERNS: dict[str, tuple[str, ...]] = {
    "excessive_ads": (
        "too many ads", "so many ads", "ad every", "forced ads", "unskippable",
        "constant ads", "ads after every", "reklam dolu", "çok fazla reklam", "her saniye reklam",
    ),
    "aggressive_paywall": (
        "pay to win", "pay2win", "p2w", "paywall", "too expensive", "subscription",
        "money grab", "greedy", "can't play without paying", "pahalı", "para tuzağı", "abonelik",
    ),
    "ux_controls_confusion": (
        "confusing", "clunky", "controls", "hard to navigate", "bad ui", "laggy",
        "unresponsive", "tutorial", "too slow", "karmaşık", "kontrol", "arayüz",
    ),
    "bugs_crashes": (
        "crash", "freezes", "bug", "glitch", "won't load", "black screen",
        "lost progress", "çöküyor", "donuyor", "açılmıyor",
    ),
    "difficulty_balance": (
        "impossible", "unfair", "difficulty spike", "stuck on level", "rigged",
        "repetitive", "boring after", "zorlaşıyor", "tekrar ediyor",
    ),
}

REVIEW_PRAISE_PATTERNS: dict[str, tuple[str, ...]] = {
    "addictive_core_loop": (
        "addictive", "addicting", "can't stop", "fun to play", "hooked", "bağımlılık", "çok eğlenceli",
    ),
    "satisfying_feel": (
        "satisfying", "smooth", "responsive", "juicy", "relaxing", "akıcı", "rahatlatıcı",
    ),
    "clean_ui_visuals": (
        "clean ui", "great graphics", "beautiful", "intuitive", "easy to use", "tasarım harika", "sade",
    ),
    "fair_monetization": (
        "no forced ads", "fair", "not pay to win", "worth the price", "free to play friendly", "reklamsız",
    ),
}
