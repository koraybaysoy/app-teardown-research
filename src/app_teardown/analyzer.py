"""Automated product teardown signal analyzer and cross-competitor market synthesizer."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from .config import (
    AD_FORMAT_PATTERNS,
    GAME_CATEGORY_HINTS,
    GAME_QUERY_HINTS,
    RETENTION_HOOK_PATTERNS,
    REVIEW_FRICTION_PATTERNS,
    REVIEW_PRAISE_PATTERNS,
)
from .models import CompetitorRecord, ProductSignals


def detect_product_mode(
    query: str = "",
    category: str = "",
    secondary_categories: list[str] | None = None,
    description: str = "",
    explicit_mode: str = "auto",
) -> str:
    """Resolve whether a target should be analyzed with the 'game' or 'app' rubric."""
    if explicit_mode in ("game", "app"):
        return explicit_mode

    cats = " ".join([category or "", *(secondary_categories or [])]).lower()
    if any(hint in cats for hint in GAME_CATEGORY_HINTS):
        return "game"

    q_low = (query or "").lower()
    if any(hint in q_low for hint in GAME_QUERY_HINTS):
        return "game"

    desc_low = (description or "").lower()[:1200]
    game_hits = sum(1 for kw in ("gameplay", "levels", "boss", "unlock levels", "play offline", "high score", "arcade") if kw in desc_low)
    if game_hits >= 2:
        return "game"
    return "app"


def _match_lexicon(text: str, patterns: dict[str, tuple[str, ...]]) -> dict[str, int]:
    low = (text or "").lower()
    found: dict[str, int] = {}
    for label, terms in patterns.items():
        cnt = sum(1 for t in terms if t in low)
        if cnt > 0:
            found[label] = cnt
    return found


def analyze_competitor(record: CompetitorRecord, explicit_mode: str = "auto", query: str = "") -> ProductSignals:
    """Compute monetization, ad-format, retention, review sentiment, and evidence scores."""
    mode = detect_product_mode(
        query=query,
        category=record.category,
        secondary_categories=record.secondary_categories,
        description=record.description,
        explicit_mode=explicit_mode,
    )
    record.product_mode = mode

    reviews_blob = "\n".join(f"{r.title} {r.text}" for r in record.reviews)
    meta_blob = "\n".join([
        record.title,
        record.subtitle_or_short_desc,
        record.description,
        record.whats_new,
        " ".join(i.name for i in record.iap_items),
    ])
    full_blob = f"{meta_blob}\n{reviews_blob}"

    # 1. Ad formats
    ad_hits = _match_lexicon(full_blob, AD_FORMAT_PATTERNS)
    detected_ads = list(ad_hits.keys())
    if record.ad_supported is True and not detected_ads:
        detected_ads.append("ad_supported_store_flag")

    # 2. IAP ladder & pricing flags
    tier_counts: Counter[str] = Counter()
    prices: list[float] = []
    for item in record.iap_items:
        tier_counts[item.tier] += 1
        if item.numeric_price is not None and item.numeric_price > 0:
            prices.append(item.numeric_price)

    has_sub = tier_counts["subscription"] > 0 or any(
        k in meta_blob.lower() for k in ("subscription", "auto-renew", "free trial", "monthly", "yearly", "annual plan")
    )
    has_remove_ads = tier_counts["remove_ads"] > 0 or "no_ads_iap" in ad_hits
    has_pass = tier_counts["pass"] > 0 or any(k in meta_blob.lower() for k in ("battle pass", "season pass", "vip pass"))

    # Classify monetization model
    if not record.free and record.price > 0:
        monetization = "Premium Paid + IAP" if record.offers_iap else "Premium Paid"
    elif has_sub and (record.ad_supported or detected_ads):
        monetization = "Hybrid (Subscription + Ads)"
    elif has_sub:
        monetization = "Freemium Subscription"
    elif record.offers_iap and (record.ad_supported or bool(detected_ads)):
        monetization = "Hybrid (IAA + IAP)"
    elif record.offers_iap:
        monetization = "Free-to-Play (IAP-Driven)"
    elif record.ad_supported or detected_ads:
        monetization = "Ad-Supported (IAA)"
    else:
        monetization = "Free / Unverified Monetization"

    # 3. Retention hooks
    ret_hits = _match_lexicon(full_blob, RETENTION_HOOK_PATTERNS)
    retention_hooks = sorted(ret_hits.keys(), key=lambda k: ret_hits[k], reverse=True)

    # 4. Review friction & praise themes (counted per review to avoid single-review inflation)
    friction_counts: Counter[str] = Counter()
    praise_counts: Counter[str] = Counter()
    ad_review_count = 0
    paywall_review_count = 0
    total_revs = len(record.reviews)

    for rev in record.reviews:
        r_text = f"{rev.title} {rev.text}".lower()
        r_frictions = _match_lexicon(r_text, REVIEW_FRICTION_PATTERNS)
        for theme in r_frictions:
            friction_counts[theme] += 1
        if "excessive_ads" in r_frictions:
            ad_review_count += 1
        if "aggressive_paywall" in r_frictions:
            paywall_review_count += 1
        r_praises = _match_lexicon(r_text, REVIEW_PRAISE_PATTERNS)
        for theme in r_praises:
            praise_counts[theme] += 1

    ad_complaint_pct = round((ad_review_count / total_revs) * 100.0, 1) if total_revs else 0.0
    paywall_complaint_pct = round((paywall_review_count / total_revs) * 100.0, 1) if total_revs else 0.0

    # 5. Popularity & Evidence completeness score (0-100)
    pop_score = round(
        math.log10(max(record.min_installs, 1)) * 6.5
        + math.log10(max(record.ratings_count, 1)) * 7.0
        + max(record.rating, 0.0) * 3.0,
        2,
    )

    ev_score = 0
    if record.description:
        ev_score += 15
    if record.reviews:
        ev_score += 15
    if record.icon_asset and record.icon_asset.downloaded:
        ev_score += 10
    if record.screenshots:
        ev_score += 10
    total_frames = sum(len(v.frames) for v in record.youtube_videos)
    if total_frames >= 12:
        ev_score += 25
    elif total_frames > 0:
        ev_score += 15
    if record.combined_palette:
        ev_score += 10
    if record.web_evidence:
        ev_score += 15

    signals = ProductSignals(
        product_mode=mode,
        monetization_model=monetization,
        detected_ad_formats=detected_ads,
        iap_tiers=dict(tier_counts),
        iap_price_min=min(prices) if prices else None,
        iap_price_max=max(prices) if prices else None,
        has_subscription=has_sub,
        has_remove_ads=has_remove_ads,
        has_battle_pass=has_pass,
        retention_hooks=retention_hooks,
        ux_friction_themes=dict(friction_counts.most_common()),
        praise_themes=dict(praise_counts.most_common()),
        ad_complaint_ratio_pct=ad_complaint_pct,
        paywall_complaint_ratio_pct=paywall_complaint_pct,
        popularity_score=pop_score,
        evidence_score=min(100, ev_score),
    )
    record.signals = signals
    return signals


def compute_cross_analysis(competitors: list[CompetitorRecord]) -> dict[str, Any]:
    """Aggregate patterns across all analyzed competitors for executive synthesis."""
    if not competitors:
        return {"total_competitors": 0}

    monetization_counter: Counter[str] = Counter()
    ad_format_counter: Counter[str] = Counter()
    retention_counter: Counter[str] = Counter()
    friction_counter: Counter[str] = Counter()
    praise_counter: Counter[str] = Counter()
    temp_counter: Counter[str] = Counter()
    mode_counter: Counter[str] = Counter()

    total_frames = 0
    total_web_sources = 0
    ratings: list[float] = []
    all_min_prices: list[float] = []
    all_max_prices: list[float] = []
    dominant_hex_pool: Counter[str] = Counter()

    for comp in competitors:
        sig = comp.signals
        mode_counter[sig.product_mode] += 1
        monetization_counter[sig.monetization_model] += 1
        for af in sig.detected_ad_formats:
            ad_format_counter[af] += 1
        for rh in sig.retention_hooks:
            retention_counter[rh] += 1
        for ft, cnt in sig.ux_friction_themes.items():
            friction_counter[ft] += cnt
        for pt, cnt in sig.praise_themes.items():
            praise_counter[pt] += cnt
        if comp.rating > 0:
            ratings.append(comp.rating)
        if sig.iap_price_min is not None:
            all_min_prices.append(sig.iap_price_min)
        if sig.iap_price_max is not None:
            all_max_prices.append(sig.iap_price_max)
        total_frames += sum(len(v.frames) for v in comp.youtube_videos)
        total_web_sources += len(comp.web_evidence)
        for sw in comp.combined_palette[:4]:
            temp_counter[sw.temperature] += 1
            dominant_hex_pool[sw.hex] += 1

    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0
    avg_evidence = round(sum(c.signals.evidence_score for c in competitors) / len(competitors), 1)
    dominant_mode = mode_counter.most_common(1)[0][0] if mode_counter else "game"
    dominant_monetization = monetization_counter.most_common(1)[0][0] if monetization_counter else "Unknown"

    return {
        "total_competitors": len(competitors),
        "dominant_mode": dominant_mode,
        "dominant_monetization": dominant_monetization,
        "monetization_breakdown": dict(monetization_counter.most_common()),
        "ad_format_adoption": dict(ad_format_counter.most_common()),
        "retention_pillars": dict(retention_counter.most_common()),
        "shared_ux_frictions": dict(friction_counter.most_common()),
        "top_praise_drivers": dict(praise_counter.most_common()),
        "color_temperature_mix": dict(temp_counter.most_common()),
        "sample_dominant_hexes": [hx for hx, _ in dominant_hex_pool.most_common(12)],
        "avg_rating": avg_rating,
        "avg_evidence_score": avg_evidence,
        "total_gameplay_frames": total_frames,
        "total_web_evidence_sources": total_web_sources,
        "iap_entry_price_range": [min(all_min_prices), max(all_min_prices)] if all_min_prices else [],
        "iap_top_price_range": [min(all_max_prices), max(all_max_prices)] if all_max_prices else [],
    }
