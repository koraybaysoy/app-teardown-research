"""Dual-store discovery and deep listing harvester (Google Play + Apple App Store)."""

from __future__ import annotations

import json
import logging
import math
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from google_play_scraper import Sort, app as gp_app, reviews as gp_reviews, search as gp_search
from PIL import Image, ImageDraw, ImageOps

from .config import (
    DOWNLOAD_TIMEOUT_SEC,
    MAX_DOWNLOAD_WORKERS,
    MAX_IMAGE_BYTES,
    REQUEST_TIMEOUT_SEC,
)
from .models import CompetitorRecord, IAPItem, ImageAsset, ReviewSample
from .utils import (
    create_http_session,
    http_get_json,
    parse_installs_int,
    parse_price_float,
    safe_join,
    slugify,
    validate_asset_url,
)

logger = logging.getLogger(__name__)


def _classify_iap_tier(name: str, numeric_price: float | None) -> str:
    low = (name or "").lower()
    if any(k in low for k in ("no ads", "remove ads", "ad free", "ad-free", "reklamsız", "reklam")):
        return "remove_ads"
    if any(k in low for k in ("pass", "season", "vip", "club")):
        return "pass"
    if any(k in low for k in ("monthly", "yearly", "annual", "weekly", "pro", "premium", "plus", "subscription", "abonelik")):
        return "subscription"
    if any(k in low for k in ("starter", "welcome", "beginner", "new player")):
        return "starter"
    if numeric_price is None:
        return "other"
    if numeric_price <= 2.49:
        return "micro"
    if numeric_price <= 6.99:
        return "starter"
    if numeric_price <= 24.99:
        return "mid"
    return "whale"


def _upgrade_google_image_url(url: str | None, target_size: str = "w2560-h1440") -> str:
    if not url or not isinstance(url, str):
        return ""
    cleaned = url.strip()
    if "=" in cleaned.rsplit("/", 1)[-1]:
        return f"{cleaned.rsplit('=', 1)[0]}={target_size}"
    return f"{cleaned}={target_size}"


def _upgrade_apple_image_url(url: str | None, target_width: int = 1284) -> str:
    if not url or not isinstance(url, str):
        return ""
    cleaned = url.strip()
    if "{w}" in cleaned and "{h}" in cleaned:
        return (
            cleaned.replace("{w}", str(target_width))
            .replace("{h}", str(target_width))
            .replace("{c}", "bb")
            .replace("{f}", "png")
        )
    return re.sub(r"/\d+x\d+bb\.(jpg|jpeg|webp)$", "/1024x1024bb.png", cleaned)


def _normalize_youtube_url(raw_url: str | None) -> str:
    if not raw_url or not isinstance(raw_url, str):
        return ""
    url = raw_url.strip()
    m = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]{6,15})", url)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return url


def _format_timestamp(ts: Any) -> str:
    if isinstance(ts, (int, float)) and ts > 0:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    if isinstance(ts, str):
        return ts.strip()
    return ""


def _popularity_rank_score(
    search_rank: int,
    installs: int = 0,
    ratings_count: int = 0,
    rating: float = 0.0,
) -> float:
    """Blend store search relevance with installs/ratings volume to surface truly popular leaders."""
    rank_bonus = max(0.0, 28.0 - (search_rank * 2.2))
    install_score = math.log10(max(installs, 1)) * 6.5 if installs > 0 else 0.0
    ratings_score = math.log10(max(ratings_count, 1)) * 7.0 if ratings_count > 0 else 0.0
    rating_bonus = max(0.0, rating) * 2.0
    return round(rank_bonus + install_score + ratings_score + rating_bonus, 2)


def discover_google_play(
    query: str,
    lang: str = "en",
    country: str = "us",
    limit: int = 5,
    rank_by_popularity: bool = True,
) -> list[dict[str, Any]]:
    """Search Google Play and optionally rank candidates by popularity + relevance."""
    pool_size = min(max(limit * 3, 12), 30)
    hits = gp_search(query, lang=lang, country=country, n_hits=pool_size)
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for idx, item in enumerate(hits):
        app_id = item.get("appId")
        if not app_id or app_id in seen_ids:
            continue
        seen_ids.add(app_id)
        installs_str = str(item.get("installs") or "")
        min_installs = parse_installs_int(installs_str)
        rating = round(float(item.get("score") or 0.0), 2)
        pop_score = _popularity_rank_score(
            search_rank=idx,
            installs=min_installs,
            rating=rating,
        )
        candidates.append({
            "store": "google_play",
            "app_id": app_id,
            "title": str(item.get("title") or "").strip(),
            "developer": str(item.get("developer") or "").strip(),
            "rating": rating,
            "installs": installs_str,
            "min_installs": min_installs,
            "free": bool(item.get("free", True)),
            "price": float(item.get("price") or 0.0),
            "icon_url": item.get("icon") or "",
            "popularity_score": pop_score,
            "store_url": f"https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}",
        })
    if rank_by_popularity:
        candidates.sort(key=lambda c: c["popularity_score"], reverse=True)
    return candidates[:limit]


def discover_app_store(
    query: str,
    country: str = "us",
    lang: str = "en",
    limit: int = 5,
    rank_by_popularity: bool = True,
) -> list[dict[str, Any]]:
    """Search Apple App Store via iTunes Search API and rank leaders by popularity + relevance."""
    session = create_http_session(lang=lang, country=country)
    pool_size = min(max(limit * 3, 15), 30)
    payload = http_get_json(
        session,
        "https://itunes.apple.com/search",
        params={
            "term": query,
            "country": country.lower(),
            "entity": "software",
            "limit": pool_size,
        },
    )
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for idx, item in enumerate(payload.get("results") or []):
        track_id = item.get("trackId")
        if not track_id:
            continue
        tid = str(track_id)
        if tid in seen_ids:
            continue
        seen_ids.add(tid)
        rating = round(float(item.get("averageUserRating") or 0.0), 2)
        ratings_count = int(item.get("userRatingCount") or 0)
        pop_score = _popularity_rank_score(
            search_rank=idx,
            ratings_count=ratings_count,
            rating=rating,
        )
        candidates.append({
            "store": "apple_app_store",
            "app_id": tid,
            "bundle_id": str(item.get("bundleId") or ""),
            "title": str(item.get("trackName") or "").strip(),
            "developer": str(item.get("artistName") or "").strip(),
            "category": str(item.get("primaryGenreName") or ""),
            "rating": rating,
            "ratings_count": ratings_count,
            "free": float(item.get("price") or 0.0) == 0.0,
            "price": float(item.get("price") or 0.0),
            "icon_url": item.get("artworkUrl512") or item.get("artworkUrl100") or "",
            "popularity_score": pop_score,
            "store_url": str(item.get("trackViewUrl") or f"https://apps.apple.com/{country.lower()}/app/id{tid}"),
        })
    if rank_by_popularity:
        candidates.sort(key=lambda c: c["popularity_score"], reverse=True)
    return candidates[:limit]


def fetch_google_play_competitor(
    app_id: str,
    lang: str = "en",
    country: str = "us",
    review_count: int = 30,
) -> CompetitorRecord:
    """Fetch detailed Google Play listing metadata, IAP/ad flags, asset URLs, and user reviews."""
    data = gp_app(app_id, lang=lang, country=country)
    title = (data.get("title") or "").strip()
    folder_name = f"gp_{slugify(title, 32)}_{slugify(app_id, 24)}"

    icon_url = _upgrade_google_image_url(data.get("icon"), "s512")
    raw_shots = [
        _upgrade_google_image_url(u, "w1920-h1080")
        for u in (data.get("screenshots") or [])
        if isinstance(u, str) and u.strip()
    ]
    screenshot_urls: list[str] = []
    seen_bases: set[str] = set()
    for u in raw_shots:
        base = u.rsplit("=", 1)[0]
        if base not in seen_bases:
            seen_bases.add(base)
            screenshot_urls.append(u)

    store_videos: list[str] = []
    raw_video = _normalize_youtube_url(data.get("video"))
    if raw_video:
        store_videos.append(raw_video)

    categories: list[str] = []
    for cat in data.get("categories") or []:
        if isinstance(cat, dict) and cat.get("name"):
            categories.append(str(cat["name"]))
    primary_cat = str(data.get("genre") or (categories[0] if categories else ""))
    secondary_cats = [c for c in categories if c != primary_cat]

    reviews: list[ReviewSample] = []
    if review_count > 0:
        try:
            revs, _ = gp_reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.MOST_RELEVANT,
                count=review_count,
            )
            for rv in revs:
                at = rv.get("at")
                reviews.append(ReviewSample(
                    author=str(rv.get("userName") or ""),
                    rating=int(rv.get("score") or 0),
                    text=str(rv.get("content") or ""),
                    date=at.strftime("%Y-%m-%d") if hasattr(at, "strftime") else str(at or ""),
                    version=str(rv.get("reviewCreatedVersion") or ""),
                    thumbs_up=int(rv.get("thumbsUpCount") or 0),
                    developer_reply=str(rv.get("replyContent") or ""),
                ))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Google Play reviews fetch failed for %s: %s", app_id, exc)

    iap_range = str(data.get("inAppProductPrice") or "")
    iap_items: list[IAPItem] = []
    if iap_range:
        # Google Play reports price range string (e.g. "$0.99 - $99.99 per item")
        parts = [p.strip() for p in re.split(r"\s*[-–]\s*", iap_range) if p.strip()]
        if len(parts) == 2:
            pmin = parse_price_float(parts[0])
            pmax = parse_price_float(parts[1])
            iap_items.append(IAPItem(name="Entry IAP Tier", price=parts[0], numeric_price=pmin, tier=_classify_iap_tier("entry", pmin)))
            iap_items.append(IAPItem(name="Top IAP Tier", price=parts[1], numeric_price=pmax, tier=_classify_iap_tier("top", pmax)))
        elif parts:
            p0 = parse_price_float(parts[0])
            iap_items.append(IAPItem(name="Standard IAP", price=parts[0], numeric_price=p0, tier=_classify_iap_tier("standard", p0)))

    return CompetitorRecord(
        store="google_play",
        app_id=app_id,
        folder_name=folder_name,
        country=country.lower(),
        lang=lang.lower(),
        store_url=data.get("url") or f"https://play.google.com/store/apps/details?id={app_id}&hl={lang}&gl={country}",
        title=title,
        subtitle_or_short_desc=(data.get("summary") or "").strip(),
        description=(data.get("description") or "").strip(),
        developer=(data.get("developer") or "").strip(),
        category=primary_cat,
        secondary_categories=secondary_cats,
        rating=round(float(data.get("score") or 0.0), 2),
        ratings_count=int(data.get("ratings") or 0),
        reviews_count=int(data.get("reviews") or 0),
        installs=str(data.get("installs") or ""),
        min_installs=int(data.get("minInstalls") or 0),
        price=float(data.get("price") or 0.0),
        currency=str(data.get("currency") or "USD"),
        free=bool(data.get("free", True)),
        offers_iap=bool(data.get("offersIAP", False)),
        iap_price_range=iap_range,
        iap_items=iap_items,
        ad_supported=data.get("containsAds"),
        content_rating=str(data.get("contentRating") or ""),
        version=str(data.get("version") or ""),
        released_date=str(data.get("released") or ""),
        last_updated=_format_timestamp(data.get("updated")),
        whats_new=(data.get("recentChanges") or "").strip(),
        icon_url=icon_url,
        screenshot_urls=screenshot_urls[:10],
        store_video_urls=store_videos,
        reviews=reviews,
        fetched_at=datetime.now(tz=timezone.utc).isoformat(),
    )


def _walk_apple_ssr(node: Any, state: dict[str, Any], target_app_id: str = "") -> None:
    if isinstance(node, dict):
        sub = node.get("subtitle")
        is_event = any(k in node for k in ("badge", "eventStartDate", "eventEndDate", "appEventId"))
        if isinstance(sub, str) and not is_event:
            sc = sub.strip()
            if 2 <= len(sc) <= 32 and sc.lower() not in ("free", "get", "in-app purchases", "open"):
                node_id = str(node.get("adamId") or node.get("id") or "")
                if target_app_id and node_id == target_app_id:
                    state["subtitle"] = sc
                elif not state["subtitle"] and ("lockup" in str(node.get("$kind") or "").lower() or "appName" in node):
                    state["subtitle"] = sc

        if node.get("title") in ("In-App Purchases", "Uygulama İçi Satın Alımlar") and isinstance(node.get("items"), list):
            for sub_item in node["items"]:
                if isinstance(sub_item, dict):
                    label = sub_item.get("title") or sub_item.get("text") or sub_item.get("leadingText")
                    price = sub_item.get("trailingText") or sub_item.get("price") or sub_item.get("subtitle") or ""
                    if isinstance(label, str) and label.strip():
                        state["iaps"].append((label.strip(), str(price).strip()))

        for key in ("videoUrl", "previewUrl", "hlsUrl"):
            val = node.get(key)
            if isinstance(val, str) and (".m3u8" in val or ".mp4" in val) and ("apple.com" in val or "mzstatic.com" in val):
                state["videos"].append(val)

        for v in node.values():
            _walk_apple_ssr(v, state, target_app_id=target_app_id)
    elif isinstance(node, list):
        for item in node:
            _walk_apple_ssr(item, state, target_app_id=target_app_id)


def _scrape_apple_extras(session, app_id: str, country: str) -> dict[str, Any]:
    extras: dict[str, Any] = {"subtitle": "", "iaps": [], "videos": []}
    url = f"https://apps.apple.com/{country.lower()}/app/id{app_id}?platform=iphone"
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT_SEC)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            h2 = soup.select_one("h2.product-header__subtitle, h2.subtitle")
            if h2 and h2.get_text(strip=True):
                extras["subtitle"] = h2.get_text(strip=True)
            script_tag = soup.find("script", id="serialized-server-data")
            if script_tag and script_tag.string:
                try:
                    _walk_apple_ssr(json.loads(script_tag.string), extras, target_app_id=app_id)
                except json.JSONDecodeError:
                    pass
            if not extras["iaps"]:
                for li in soup.select("li.list-with-numbers__item"):
                    name_el = li.select_one(".list-with-numbers__item__title")
                    price_el = li.select_one(".list-with-numbers__item__price")
                    if name_el:
                        extras["iaps"].append((
                            name_el.get_text(strip=True),
                            price_el.get_text(strip=True) if price_el else "",
                        ))
    except Exception as exc:  # noqa: BLE001
        logger.debug("Apple SSR extras error for %s: %s", app_id, exc)

    # Deduplicate IAPs
    seen_names: set[str] = set()
    dedup_iaps: list[tuple[str, str]] = []
    for n, p in extras["iaps"]:
        if n not in seen_names:
            seen_names.add(n)
            dedup_iaps.append((n, p))
    extras["iaps"] = dedup_iaps[:15]
    extras["videos"] = list(dict.fromkeys(extras["videos"]))[:2]
    return extras


def _fetch_apple_reviews(session, app_id: str, country: str, limit: int = 30) -> list[ReviewSample]:
    url = f"https://itunes.apple.com/{country.lower()}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
    samples: list[ReviewSample] = []
    try:
        payload = http_get_json(session, url)
        entries = (payload.get("feed") or {}).get("entry") or []
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            if not isinstance(entry, dict) or "im:rating" not in entry:
                continue
            samples.append(ReviewSample(
                author=str(((entry.get("author") or {}).get("name") or {}).get("label") or ""),
                rating=int((entry.get("im:rating") or {}).get("label") or 0),
                title=str((entry.get("title") or {}).get("label") or ""),
                text=str((entry.get("content") or {}).get("label") or ""),
                date=str((entry.get("updated") or {}).get("label") or "")[:10],
                version=str((entry.get("im:version") or {}).get("label") or ""),
                thumbs_up=int((entry.get("im:voteSum") or {}).get("label") or 0),
            ))
            if len(samples) >= limit:
                break
    except Exception as exc:  # noqa: BLE001
        logger.debug("Apple RSS reviews error for %s: %s", app_id, exc)
    return samples


def fetch_app_store_competitor(
    app_id: str,
    country: str = "us",
    lang: str = "en",
    review_count: int = 30,
) -> CompetitorRecord:
    """Fetch complete Apple App Store listing, IAP table, screenshots, and reviews."""
    clean_id = re.sub(r"\D+", "", str(app_id))
    if not clean_id:
        raise ValueError(f"Invalid Apple App Store ID: {app_id!r}")
    session = create_http_session(lang=lang, country=country)
    lookup = http_get_json(
        session,
        "https://itunes.apple.com/lookup",
        params={"id": clean_id, "country": country.lower()},
    )
    results = lookup.get("results") or []
    if not results:
        raise ValueError(f"Apple App Store app not found: id={clean_id} country={country}")
    info = results[0]
    extras = _scrape_apple_extras(session, clean_id, country)
    reviews = _fetch_apple_reviews(session, clean_id, country, limit=review_count) if review_count > 0 else []

    title = str(info.get("trackName") or "").strip()
    folder_name = f"ios_{slugify(title, 32)}_{clean_id}"
    genres = [str(g) for g in (info.get("genres") or []) if g]
    primary_cat = str(info.get("primaryGenreName") or (genres[0] if genres else ""))
    secondary_cats = [g for g in genres if g != primary_cat]

    iap_items: list[IAPItem] = []
    for name, price in extras["iaps"]:
        num = parse_price_float(price)
        iap_items.append(IAPItem(name=name, price=price, numeric_price=num, tier=_classify_iap_tier(name, num)))

    prices = [i.numeric_price for i in iap_items if i.numeric_price is not None]
    iap_range = ""
    if prices:
        iap_range = f"{min(prices):.2f} - {max(prices):.2f} {info.get('currency') or 'USD'}"

    return CompetitorRecord(
        store="apple_app_store",
        app_id=clean_id,
        folder_name=folder_name,
        country=country.lower(),
        lang=lang.lower(),
        store_url=str(info.get("trackViewUrl") or f"https://apps.apple.com/{country.lower()}/app/id{clean_id}"),
        title=title,
        subtitle_or_short_desc=extras["subtitle"],
        description=str(info.get("description") or "").strip(),
        developer=str(info.get("artistName") or "").strip(),
        category=primary_cat,
        secondary_categories=secondary_cats,
        rating=round(float(info.get("averageUserRating") or 0.0), 2),
        ratings_count=int(info.get("userRatingCount") or 0),
        reviews_count=int(info.get("userRatingCount") or 0),
        price=float(info.get("price") or 0.0),
        currency=str(info.get("currency") or "USD"),
        free=float(info.get("price") or 0.0) == 0.0,
        offers_iap=bool(iap_items),
        iap_price_range=iap_range,
        iap_items=iap_items,
        ad_supported=None,
        content_rating=str(info.get("contentAdvisoryRating") or info.get("trackContentRating") or ""),
        version=str(info.get("version") or ""),
        released_date=str(info.get("releaseDate") or "")[:10],
        last_updated=str(info.get("currentVersionReleaseDate") or "")[:10],
        whats_new=str(info.get("releaseNotes") or "").strip(),
        icon_url=_upgrade_apple_image_url(info.get("artworkUrl512") or info.get("artworkUrl100")),
        screenshot_urls=[
            _upgrade_apple_image_url(u)
            for u in (info.get("screenshotUrls") or [])[:10]
            if isinstance(u, str) and u.strip()
        ],
        store_video_urls=extras["videos"],
        reviews=reviews,
        fetched_at=datetime.now(tz=timezone.utc).isoformat(),
    )


def _extract_top_hex(img: Image.Image, top_k: int = 4) -> list[str]:
    try:
        sample = img.convert("RGB").copy()
        sample.thumbnail((120, 120))
        quantized = sample.quantize(colors=top_k, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette() or []
        counts = sorted(quantized.getcolors() or [], key=lambda x: x[0], reverse=True)
        out: list[str] = []
        for _, idx in counts[:top_k]:
            base = idx * 3
            if base + 2 < len(palette):
                out.append(f"#{palette[base]:02X}{palette[base + 1]:02X}{palette[base + 2]:02X}")
        return out
    except Exception:  # noqa: BLE001
        return []


def _download_image(session, url: str, dest_dir: Path, stem: str, kind: str, app_dir: Path) -> ImageAsset:
    asset = ImageAsset(kind=kind, source_url=url)
    try:
        safe_url = validate_asset_url(url)
        resp = session.get(safe_url, stream=True, timeout=DOWNLOAD_TIMEOUT_SEC)
        resp.raise_for_status()
        chunks: list[bytes] = []
        total = 0
        for chunk in resp.iter_content(chunk_size=65536):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_IMAGE_BYTES:
                raise ValueError("Image exceeds max size cap")
            chunks.append(chunk)
        raw = b"".join(chunks)
        with Image.open(BytesIO(raw)) as img:
            img.load()
            fmt = (img.format or "PNG").upper()
            ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".png"}.get(fmt, ".png")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = safe_join(dest_dir, f"{stem}{ext}")
            if fmt == "WEBP":
                img.save(dest_path, format="PNG")
                fmt = "PNG"
            else:
                dest_path.write_bytes(raw)
            w, h = img.size
            asset.width = w
            asset.height = h
            asset.orientation = "square" if abs(w - h) <= 4 else ("portrait" if h > w else "landscape")
            g = math.gcd(w, h) if w > 0 and h > 0 else 1
            asset.aspect_ratio = f"{w // g}:{h // g}" if g else ""
            asset.image_format = fmt
            asset.file_size_bytes = dest_path.stat().st_size
            asset.dominant_colors = _extract_top_hex(img, top_k=4)
            asset.local_path = dest_path.relative_to(app_dir).as_posix()
            asset.downloaded = True
    except Exception as exc:  # noqa: BLE001
        asset.error = str(exc)
    return asset


def _build_screenshots_sheet(screenshots: list[ImageAsset], app_dir: Path, output_path: Path) -> str:
    valid = [
        (idx + 1, app_dir / s.local_path, s)
        for idx, s in enumerate(screenshots)
        if s.downloaded and s.local_path and (app_dir / s.local_path).exists()
    ]
    if not valid:
        return ""
    try:
        landscape = sum(1 for _, _, s in valid if s.orientation == "landscape") > len(valid) / 2
        tile_w, tile_h = (420, 236) if landscape else (240, 460)
        header_h, pad = 30, 14
        cols = 3 if landscape else min(5, max(1, len(valid)))
        rows = math.ceil(len(valid) / cols)
        sheet = Image.new("RGB", (pad + cols * (tile_w + pad), pad + rows * (tile_h + header_h + pad)), (16, 20, 28))
        draw = ImageDraw.Draw(sheet)
        for pos, (idx, img_path, shot) in enumerate(valid):
            r, c = divmod(pos, cols)
            x0 = pad + c * (tile_w + pad)
            y0 = pad + r * (tile_h + header_h + pad)
            draw.rectangle([x0, y0, x0 + tile_w, y0 + header_h - 3], fill=(34, 44, 62))
            draw.text((x0 + 8, y0 + 7), f"Store #{idx}  {shot.width}x{shot.height}", fill=(240, 245, 255))
            with Image.open(img_path) as im:
                thumb = ImageOps.contain(im.convert("RGB"), (tile_w, tile_h))
                sheet.paste(thumb, (x0 + (tile_w - thumb.width) // 2, y0 + header_h + (tile_h - thumb.height) // 2))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(output_path, format="PNG", optimize=True)
        return output_path.relative_to(app_dir).as_posix()
    except Exception:  # noqa: BLE001
        return ""


def download_store_visuals(record: CompetitorRecord, app_dir: Path, max_screenshots: int = 8) -> None:
    """Download icon and store screenshots for UI/UX reference alongside gameplay frames."""
    assets_dir = safe_join(app_dir, "assets")
    icon_dir = safe_join(assets_dir, "icon")
    shots_dir = safe_join(assets_dir, "store_screenshots")
    session = create_http_session(lang=record.lang, country=record.country)

    tasks: list[tuple[str, int, str, Path, str]] = []
    if record.icon_url:
        tasks.append(("icon", 0, record.icon_url, icon_dir, "icon"))
    for idx, url in enumerate(record.screenshot_urls[:max_screenshots], start=1):
        tasks.append(("screenshot", idx, url, shots_dir, f"{idx:02d}"))

    shot_map: dict[int, ImageAsset] = {}
    with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as pool:
        fmap = {
            pool.submit(_download_image, session, u, d, stem, kind, app_dir): (kind, idx)
            for kind, idx, u, d, stem in tasks
        }
        for fut in as_completed(fmap):
            kind, idx = fmap[fut]
            res = fut.result()
            if kind == "icon":
                record.icon_asset = res
            else:
                shot_map[idx] = res

    record.screenshots = [shot_map[i] for i in sorted(shot_map)]
    if record.screenshots:
        record.screenshots_sheet_path = _build_screenshots_sheet(
            record.screenshots, app_dir, safe_join(assets_dir, "store_screenshots_sheet.png")
        )
