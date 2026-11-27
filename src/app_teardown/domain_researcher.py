"""Real-world domain subject researcher: encyclopedic knowledge (Wikipedia + DDG) and SSRF-safe visual reference photo harvester (Bing Images + Wikimedia Commons + Openverse)."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageOps

from .config import (
    DEFAULT_MAX_DOMAIN_IMAGES,
    DOWNLOAD_TIMEOUT_SEC,
    MAX_REFERENCE_IMAGE_BYTES,
    MIN_REFERENCE_IMAGE_DIM,
    REQUEST_TIMEOUT_SEC,
    WATERMARKED_STOCK_DOMAINS,
    WIKIMEDIA_USER_AGENT,
)
from .frame_extractor import extract_palette_swatches, load_ui_font, render_palette_card
from .models import ColorSwatch, DomainEvidenceItem, DomainReferenceImage
from .utils import (
    create_http_session,
    fetch_public_image_bytes,
    is_url_allowed_by_robots,
    safe_join,
    sanitize_untrusted_text,
    slugify,
    validate_public_image_url,
    validate_public_web_url,
)
from .web_researcher import search_duckduckgo_html

logger = logging.getLogger(__name__)


def classify_domain_category(topic: str) -> str:
    """Classify a domain research query into a structured real-world knowledge pillar."""
    low = (topic or "").lower()
    if any(k in low for k in (
        "brand", "marka", "mcdonald", "burger king", "whopper", "big mac", "shake shack",
        "five guys", "in-n-out", "starbucks", "chanel", "dior", "creed", "famous", "ünlü",
        "iconic", "domino", "krispy", "nike", "porsche", "ferrari", "ritz",
    )):
        return "famous_brands"
    if any(k in low for k in (
        "layer", "katman", "anatomy", "anatomi", "ingredient", "malzeme", "component",
        "parça", "topping", "order", "sıra", "structure", "pyramid", "notes", "parts",
    )):
        return "anatomy_layers"
    if any(k in low for k in (
        "how ", "nasıl", "made", "yapılır", "process", "süreç", "stage", "aşama",
        "cook", "grill", "pişir", "bake", "brew", "craft", "step", "preparation", "recipe",
        "workflow", "maceration",
    )):
        return "how_its_made"
    if any(k in low for k in (
        "what is", "nedir", "definition", "gerçek hayat", "real world", "real-world",
        "equivalent", "overview", "origin", "history", "fundamentals", "psychology",
    )):
        return "what_is_it"
    return "real_world_equivalent"


def _create_wikimedia_session(lang: str = "en", country: str = "us"):
    session = create_http_session(lang=lang, country=country)
    session.headers["User-Agent"] = WIKIMEDIA_USER_AGENT
    return session


def _is_watermarked_stock_domain(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in WATERMARKED_STOCK_DOMAINS)


def _strip_html_tags(raw: str) -> str:
    if not raw:
        return ""
    return BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)


def _parse_wikipedia_sections(full_text: str) -> list[tuple[str, str]]:
    """Split a plain-text Wikipedia article into (section_title, body) pairs."""
    if not full_text:
        return []
    parts = re.split(r"(?m)^\s*==\s*([^=\n]+?)\s*==\s*$", full_text)
    sections: list[tuple[str, str]] = []
    intro = re.sub(r"\s*===[^=\n]+===\s*", " ", parts[0]).strip()
    if intro:
        sections.append(("Overview", intro))
    for i in range(1, len(parts) - 1, 2):
        sec_title = parts[i].strip()
        sec_body = re.sub(r"\s*===[^=\n]+===\s*", " ", parts[i + 1]).strip()
        if sec_title and sec_body:
            sections.append((sec_title, sec_body))
    return sections


def _classify_wiki_section_pillar(sec_title: str) -> str | None:
    low = sec_title.lower()
    if any(k in low for k in ("ingredient", "composition", "structure", "layer", "anatomy", "type", "variet", "variation", "component", "note", "part")):
        return "anatomy_layers"
    if any(k in low for k in ("prepar", "cook", "making", "process", "product", "manufactur", "method", "brew", "craft", "assembl", "serv")):
        return "how_its_made"
    if any(k in low for k in ("brand", "chain", "restaurant", "market", "industry", "culture", "popular")):
        return "real_world_equivalent"
    return None


def search_wikipedia_knowledge(
    query: str,
    category: str = "what_is_it",
    wiki_lang: str = "en",
    max_articles: int = 1,
    extract_sections: bool = False,
) -> list[DomainEvidenceItem]:
    """Fetch clean encyclopedic real-world definitions, preparation, and component sections from Wikipedia API."""
    clean_q = (query or "").strip()
    if not clean_q:
        return []
    wl = re.sub(r"[^a-z]", "", (wiki_lang or "en").lower())[:3] or "en"
    api_url = f"https://{wl}.wikipedia.org/w/api.php"
    session = _create_wikimedia_session(lang=wl)
    now_iso = datetime.now(tz=timezone.utc).isoformat()
    results: list[DomainEvidenceItem] = []

    try:
        search_resp = session.get(
            api_url,
            params={
                "action": "query",
                "list": "search",
                "srsearch": clean_q,
                "srlimit": max(2, max_articles + 1),
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if search_resp.status_code != 200:
            return []
        hits = (search_resp.json().get("query") or {}).get("search") or []
        titles: list[str] = []
        for h in hits:
            title = str(h.get("title") or "").strip()
            if not title or "(disambiguation)" in title.lower():
                continue
            titles.append(title)
            if len(titles) >= max_articles:
                break

        for title in titles:
            params: dict[str, Any] = {
                "action": "query",
                "prop": "extracts|info",
                "inprop": "url",
                "titles": title,
                "explaintext": "1",
                "redirects": "1",
                "format": "json",
            }
            if not extract_sections:
                params["exintro"] = "1"
                params["exchars"] = "1000"
            detail_resp = session.get(api_url, params=params, timeout=REQUEST_TIMEOUT_SEC)
            if detail_resp.status_code != 200:
                continue
            pages = (detail_resp.json().get("query") or {}).get("pages") or {}
            for page in pages.values():
                if not isinstance(page, dict) or page.get("missing") is not None:
                    continue
                raw_extract = str(page.get("extract") or "")
                if not raw_extract.strip():
                    continue
                canonical_title = sanitize_untrusted_text(str(page.get("title") or title), max_len=200)
                full_url = str(
                    page.get("fullurl")
                    or f"https://{wl}.wikipedia.org/wiki/{quote(canonical_title.replace(' ', '_'))}"
                )
                try:
                    safe_url = validate_public_web_url(full_url)
                except ValueError:
                    continue

                if extract_sections:
                    sections = _parse_wikipedia_sections(raw_extract)
                    if sections:
                        intro_body = sanitize_untrusted_text(sections[0][1], max_len=900)
                        if intro_body:
                            results.append(DomainEvidenceItem(
                                topic=clean_q,
                                query=clean_q,
                                title=f"{canonical_title} - Overview (Wikipedia)",
                                url=safe_url,
                                domain=f"{wl}.wikipedia.org",
                                snippet=intro_body,
                                fetched_at=now_iso,
                                category=category,
                                source_engine="wikipedia",
                            ))
                        added_pillars: set[str] = set()
                        for sec_title, sec_body in sections[1:]:
                            pillar = _classify_wiki_section_pillar(sec_title)
                            if not pillar or pillar in added_pillars:
                                continue
                            clean_body = sanitize_untrusted_text(sec_body, max_len=900)
                            if len(clean_body) < 80:
                                continue
                            added_pillars.add(pillar)
                            sec_anchor = quote(sec_title.replace(" ", "_"))
                            results.append(DomainEvidenceItem(
                                topic=f"{clean_q} ({sec_title})",
                                query=clean_q,
                                title=f"{canonical_title}: {sec_title} (Wikipedia)",
                                url=f"{safe_url}#{sec_anchor}",
                                domain=f"{wl}.wikipedia.org",
                                snippet=clean_body,
                                fetched_at=now_iso,
                                category=pillar,
                                source_engine="wikipedia",
                            ))
                            if len(added_pillars) >= 3:
                                break
                else:
                    clean_intro = sanitize_untrusted_text(raw_extract.split("\n==")[0], max_len=900)
                    if clean_intro:
                        results.append(DomainEvidenceItem(
                            topic=clean_q,
                            query=clean_q,
                            title=f"{canonical_title} (Wikipedia)",
                            url=safe_url,
                            domain=f"{wl}.wikipedia.org",
                            snippet=clean_intro,
                            fetched_at=now_iso,
                            category=category,
                            source_engine="wikipedia",
                        ))
    except Exception as exc:  # noqa: BLE001
        logger.debug("Wikipedia knowledge lookup failed for %r: %s", clean_q, exc)
    return results


def research_domain_knowledge_structured(
    domain_topics: list[str],
    core_subject: str = "",
    famous_brands: list[str] | None = None,
    lang: str = "en",
    country: str = "us",
    max_per_topic: int = 3,
    polite_delay_sec: float = 0.35,
    official_only: bool = False,
) -> list[DomainEvidenceItem]:
    """Combine official Wikipedia real-world/brand knowledge with optional DuckDuckGo web snippets across all 4 domain pillars."""
    items: list[DomainEvidenceItem] = []
    seen_urls: set[str] = set()
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    def _add_item(item: DomainEvidenceItem) -> None:
        if not item.url or item.url in seen_urls:
            return
        seen_urls.add(item.url)
        item.evidence_id = f"EV-DOM-{len(items) + 1:02d}"
        items.append(item)

    # 1. Wikipedia core subject definition + structured preparation/ingredients/variations sections
    subj = (core_subject or "").strip()
    if subj:
        for wiki_item in search_wikipedia_knowledge(
            subj,
            category="what_is_it",
            wiki_lang="en",
            max_articles=1,
            extract_sections=True,
        ):
            _add_item(wiki_item)
        if lang.lower() not in ("en", ""):
            for local_wiki in search_wikipedia_knowledge(
                subj,
                category="what_is_it",
                wiki_lang=lang.lower(),
                max_articles=1,
                extract_sections=False,
            ):
                _add_item(local_wiki)

    # 2. Wikipedia profiles of iconic real-world famous brands (structure, ingredients, history)
    brands = [b.strip() for b in (famous_brands or []) if b and b.strip()]
    for b_idx, brand in enumerate(brands[:4]):
        if b_idx > 0 and polite_delay_sec > 0:
            time.sleep(min(polite_delay_sec, 0.25))
        for brand_item in search_wikipedia_knowledge(brand, category="famous_brands", wiki_lang="en", max_articles=1):
            _add_item(brand_item)

    # 3. Categorized web queries (DuckDuckGo HTML) skipped when official_only=True
    if not official_only:
        for idx, topic in enumerate(domain_topics):
            clean_topic = (topic or "").strip()
            if not clean_topic:
                continue
            cat = classify_domain_category(clean_topic)
            if idx > 0 and polite_delay_sec > 0:
                time.sleep(polite_delay_sec)
            hits = search_duckduckgo_html(clean_topic, max_results=max_per_topic, lang=lang, country=country)
            for hit in hits:
                _add_item(DomainEvidenceItem(
                    topic=clean_topic,
                    query=clean_topic,
                    title=hit["title"],
                    url=hit["url"],
                    domain=hit["domain"],
                    snippet=hit["snippet"],
                    fetched_at=now_iso,
                    category=cat,
                    source_engine="duckduckgo",
                ))

    # 4. If DuckDuckGo returned no results (or official_only), add targeted Wikipedia fallback for the first 2 topics
    non_wiki_count = sum(1 for i in items if i.source_engine != "wikipedia")
    if non_wiki_count == 0 and domain_topics:
        for topic in domain_topics[:2]:
            clean_topic = (topic or "").strip()
            if not clean_topic:
                continue
            cat = classify_domain_category(clean_topic)
            for fallback in search_wikipedia_knowledge(clean_topic, category=cat, wiki_lang="en", max_articles=1):
                _add_item(fallback)

    return items


# --- Multi-Engine Visual Reference Searchers ---


def search_bing_images(
    query: str,
    max_results: int = 6,
    lang: str = "en",
    country: str = "us",
) -> list[dict[str, str]]:
    """Search public Bing Images async results (zero API key, clean official brand & editorial photos)."""
    clean_q = (query or "").strip()
    if not clean_q:
        return []
    session = create_http_session(lang=lang, country=country)
    try:
        resp = session.get(
            "https://www.bing.com/images/async",
            params={
                "q": clean_q,
                "first": 0,
                "count": max(12, max_results * 2),
                "mmasync": 1,
                "adlt": "strict",
            },
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        candidates: list[tuple[int, dict[str, str]]] = []
        seen: set[str] = set()
        for idx, card in enumerate(soup.select("a.iusc")):
            raw_m = card.get("m")
            if not raw_m:
                continue
            try:
                meta = json.loads(str(raw_m))
            except json.JSONDecodeError:
                continue
            murl = str(meta.get("murl") or "").strip()
            turl = str(meta.get("turl") or "").strip()
            purl = str(meta.get("purl") or "").strip()
            title = sanitize_untrusted_text(str(meta.get("t") or ""), max_len=180)
            if not murl and not turl:
                continue
            primary_url = murl or turl
            try:
                safe_img = validate_public_image_url(primary_url, resolve_dns=False)
            except ValueError:
                if turl:
                    try:
                        safe_img = validate_public_image_url(turl, resolve_dns=False)
                    except ValueError:
                        continue
                else:
                    continue
            if safe_img in seen:
                continue
            seen.add(safe_img)

            safe_thumb = ""
            if turl:
                try:
                    safe_thumb = validate_public_image_url(turl, resolve_dns=False)
                except ValueError:
                    safe_thumb = ""

            safe_page = ""
            if purl:
                try:
                    safe_page = validate_public_web_url(purl)
                except ValueError:
                    safe_page = ""

            domain = (urlparse(safe_page or safe_img).hostname or "").lower()
            # Prefer clean editorial / official brand photography over watermarked stock sites
            penalty = 100 if _is_watermarked_stock_domain(safe_img) or _is_watermarked_stock_domain(safe_page) else 0
            candidates.append((
                penalty + idx,
                {
                    "title": title or clean_q,
                    "image_url": safe_img,
                    "thumb_url": safe_thumb,
                    "page_url": safe_page or safe_img,
                    "domain": domain,
                    "source_engine": "bing_images",
                    "license_note": "Visual reference only (verify rights; do not copy trademarked logos or brand photography)",
                },
            ))
        candidates.sort(key=lambda pair: pair[0])
        return [c for _, c in candidates[:max_results]]
    except Exception as exc:  # noqa: BLE001
        logger.debug("Bing Images search failed for %r: %s", clean_q, exc)
        return []


def search_wikimedia_commons_images(
    query: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    """Search Wikimedia Commons official API for real-world photos and iconic product references."""
    clean_q = (query or "").strip()
    if not clean_q:
        return []
    session = _create_wikimedia_session()
    try:
        resp = session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": clean_q,
                "gsrnamespace": 6,
                "gsrlimit": max(8, max_results * 2),
                "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata",
                "iiurlwidth": 1024,
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if resp.status_code != 200:
            return []
        pages = (resp.json().get("query") or {}).get("pages") or {}
        out: list[dict[str, str]] = []
        for page in sorted(pages.values(), key=lambda p: int(p.get("index") or 999)):
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            ii = infos[0]
            mime = str(ii.get("mime") or "").lower()
            if mime not in ("image/jpeg", "image/png", "image/webp"):
                continue
            w = int(ii.get("width") or 0)
            h = int(ii.get("height") or 0)
            if w < 240 or h < 200:
                continue
            thumb_url = str(ii.get("thumburl") or "").strip()
            orig_url = str(ii.get("url") or "").strip()
            img_url = thumb_url or orig_url
            if not img_url:
                continue
            try:
                safe_img = validate_public_image_url(img_url, resolve_dns=False)
            except ValueError:
                continue
            page_url = str(ii.get("descriptionurl") or orig_url or safe_img)
            try:
                safe_page = validate_public_web_url(page_url)
            except ValueError:
                safe_page = safe_img
            extmeta = ii.get("extmetadata") or {}
            lic = _strip_html_tags(str((extmeta.get("LicenseShortName") or {}).get("value") or "Wikimedia Commons"))
            raw_title = str(page.get("title") or "").replace("File:", "")
            raw_title = re.sub(r"\.[a-zA-Z0-9]{2,5}$", "", raw_title).replace("_", " ")
            out.append({
                "title": sanitize_untrusted_text(raw_title, max_len=180) or clean_q,
                "image_url": safe_img,
                "thumb_url": safe_img,
                "page_url": safe_page,
                "domain": "commons.wikimedia.org",
                "source_engine": "wikimedia_commons",
                "license_note": f"Wikimedia Commons ({lic[:60]}) — reference only; check attribution before commercial reuse",
            })
            if len(out) >= max_results:
                break
        return out
    except Exception as exc:  # noqa: BLE001
        logger.debug("Wikimedia Commons image search failed for %r: %s", clean_q, exc)
        return []


def search_openverse_images(
    query: str,
    max_results: int = 4,
) -> list[dict[str, str]]:
    """Search Openverse CC-licensed public image API as a clean photography fallback."""
    clean_q = (query or "").strip()
    if not clean_q:
        return []
    session = _create_wikimedia_session()
    try:
        resp = session.get(
            "https://api.openverse.org/v1/images/",
            params={"q": clean_q, "page_size": max(6, max_results * 2)},
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if resp.status_code != 200:
            return []
        out: list[dict[str, str]] = []
        for item in (resp.json().get("results") or []):
            img_url = str(item.get("url") or "").strip()
            thumb_url = str(item.get("thumbnail") or "").strip()
            if not img_url:
                continue
            try:
                safe_img = validate_public_image_url(img_url, resolve_dns=False)
            except ValueError:
                continue
            safe_thumb = ""
            if thumb_url:
                try:
                    safe_thumb = validate_public_image_url(thumb_url, resolve_dns=False)
                except ValueError:
                    safe_thumb = ""
            landing = str(item.get("foreign_landing_url") or safe_img)
            try:
                safe_page = validate_public_web_url(landing)
            except ValueError:
                safe_page = safe_img
            lic = f"CC {str(item.get('license') or '').upper()} {item.get('license_version') or ''}".strip()
            out.append({
                "title": sanitize_untrusted_text(str(item.get("title") or clean_q), max_len=180),
                "image_url": safe_img,
                "thumb_url": safe_thumb,
                "page_url": safe_page,
                "domain": (urlparse(safe_page).hostname or "openverse.org").lower(),
                "source_engine": "openverse",
                "license_note": f"Openverse ({lic}) — reference only; check license before reuse",
            })
            if len(out) >= max_results:
                break
        return out
    except Exception as exc:  # noqa: BLE001
        logger.debug("Openverse image search failed for %r: %s", clean_q, exc)
        return []


# --- Image Verification, Moodboard Sheet & Real-World Palette ---


def _perceptual_fingerprint(img: Image.Image) -> str:
    """Compute a lightweight grayscale thumbnail hash to prevent saving identical images twice."""
    tiny = img.convert("L").resize((16, 16))
    return hashlib.sha256(tiny.tobytes()).hexdigest()[:16]


def _save_verified_reference_image(
    raw_bytes: bytes,
    dest_dir: Path,
    stem: str,
    run_dir: Path,
) -> tuple[Path, int, int, str, int, list[str], str]:
    """Validate raster image bytes with Pillow, normalize format, and extract dominant HEX swatches."""
    with Image.open(BytesIO(raw_bytes)) as img:
        img.load()
        # Handle animated GIF/WEBP safely by reading first frame only
        if getattr(img, "is_animated", False):
            img.seek(0)
        w, h = img.size
        if w < MIN_REFERENCE_IMAGE_DIM or h < MIN_REFERENCE_IMAGE_DIM:
            raise ValueError(f"Image too small ({w}x{h} < {MIN_REFERENCE_IMAGE_DIM}px)")

        fingerprint = _perceptual_fingerprint(img)
        rgb = img.convert("RGB")
        swatches = extract_palette_swatches([rgb], top_k=4)

        dest_dir.mkdir(parents=True, exist_ok=True)
        # Re-encode cleanly to strip any polyglot trailing bytes or exotic subformats
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
        if has_alpha:
            out_path = safe_join(dest_dir, f"{stem}.png")
            img.convert("RGBA").save(out_path, format="PNG", optimize=True)
            fmt = "PNG"
        else:
            out_path = safe_join(dest_dir, f"{stem}.jpg")
            rgb.save(out_path, format="JPEG", quality=90, optimize=True)
            fmt = "JPEG"

        size_bytes = out_path.stat().st_size
        rel_path = out_path.relative_to(run_dir).as_posix()
        return out_path, w, h, fmt, size_bytes, [s.hex for s in swatches], fingerprint


def build_domain_reference_sheet(
    references: list[DomainReferenceImage],
    run_dir: Path,
    output_path: Path,
    subject_title: str = "",
) -> str:
    """Compose a category-coded visual moodboard contact sheet for rapid multimodal AI inspection."""
    valid = [
        ref for ref in references
        if ref.downloaded and ref.local_path and (run_dir / ref.local_path).exists()
    ]
    if not valid:
        return ""
    try:
        cols = min(4, max(1, len(valid)))
        rows = math.ceil(len(valid) / cols)
        tile_w, tile_h = 340, 260
        header_h = 34
        title_bar_h = 44
        pad = 14

        canvas_w = pad + cols * (tile_w + pad)
        canvas_h = title_bar_h + pad + rows * (tile_h + header_h + pad)
        canvas = Image.new("RGB", (canvas_w, canvas_h), (13, 17, 23))
        draw = ImageDraw.Draw(canvas)

        banner_title = f"Real-World & Famous Brand Visual Reference Board - {subject_title[:56] or 'Domain Subject'}"
        banner_font = load_ui_font(16)
        tile_font = load_ui_font(13)
        draw.rectangle([0, 0, canvas_w, title_bar_h], fill=(20, 28, 42))
        draw.text((pad, 12), banner_title, fill=(242, 246, 255), font=banner_font)

        cat_styles = {
            "anatomy_layers": ((20, 96, 86), "ANATOMY"),
            "how_its_made": ((124, 78, 22), "PROCESS"),
            "real_world_equivalent": ((28, 74, 126), "REAL-WORLD"),
            "famous_brand": ((104, 38, 118), "BRAND"),
        }

        for pos, ref in enumerate(valid):
            r, c = divmod(pos, cols)
            x0 = pad + c * (tile_w + pad)
            y0 = title_bar_h + pad + r * (tile_h + header_h + pad)
            hdr_bg, tag = cat_styles.get(ref.category, ((46, 56, 74), "REF"))
            label = f"{ref.evidence_id} [{tag}] {(ref.subject_label or ref.title)[:28]}"
            draw.rectangle([x0, y0, x0 + tile_w, y0 + header_h - 2], fill=hdr_bg)
            draw.text((x0 + 8, y0 + 8), label, fill=(245, 248, 255), font=tile_font)

            draw.rectangle(
                [x0, y0 + header_h, x0 + tile_w, y0 + header_h + tile_h],
                fill=(22, 29, 40),
                outline=(48, 60, 82),
                width=1,
            )
            with Image.open(run_dir / ref.local_path) as im:
                thumb = ImageOps.contain(im.convert("RGB"), (tile_w - 6, tile_h - 6))
                canvas.paste(
                    thumb,
                    (
                        x0 + (tile_w - thumb.width) // 2,
                        y0 + header_h + (tile_h - thumb.height) // 2,
                    ),
                )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, format="PNG", optimize=True)
        return output_path.relative_to(run_dir).as_posix()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Domain reference sheet rendering failed: %s", exc)
        return ""


def harvest_domain_reference_images(
    image_queries: list[dict[str, str]],
    run_dir: Path,
    subject_title: str = "",
    max_images: int = DEFAULT_MAX_DOMAIN_IMAGES,
    lang: str = "en",
    country: str = "us",
    polite_delay_sec: float = 0.25,
    official_only: bool = False,
    respect_robots: bool = True,
) -> tuple[list[DomainReferenceImage], str, list[ColorSwatch], str]:
    """Download verified real-world & famous brand reference photos (respecting robots.txt and optional official-only APIs), build moodboard sheet & HEX palette card."""
    if not image_queries or max_images <= 0:
        return [], "", [], ""

    refs_dir = safe_join(run_dir, "assets", "domain_references")
    refs_dir.mkdir(parents=True, exist_ok=True)

    session = create_http_session(lang=lang, country=country)
    wiki_session = _create_wikimedia_session(lang=lang, country=country)

    saved: list[DomainReferenceImage] = []
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()

    # Distribute budget evenly so anatomy, process, real-world, and famous brands are all represented
    num_queries = len(image_queries)
    per_query_target = max(1, math.ceil(max_images / max(1, num_queries)))

    for q_idx, spec in enumerate(image_queries):
        if len(saved) >= max_images:
            break
        q_str = (spec.get("query") or "").strip()
        if not q_str:
            continue
        category = (spec.get("category") or "real_world_equivalent").strip()
        label = (spec.get("label") or q_str[:48]).strip()
        slot_cap = min(
            int(spec.get("count") or per_query_target),
            max_images - len(saved),
        )

        if q_idx > 0 and polite_delay_sec > 0:
            time.sleep(polite_delay_sec)

        # Official-only mode strictly uses open-licensed Wikimedia Commons + Openverse APIs (no Bing scraping)
        candidates: list[dict[str, str]] = []
        if official_only:
            # Strip trailing generic filler words like "product photo" so Commons/Openverse match better
            clean_api_q = re.sub(r"\b(product photo|high quality photography|close up)\b", "", q_str, flags=re.IGNORECASE).strip() or q_str
            candidates.extend(search_wikimedia_commons_images(clean_api_q, max_results=5))
            if len(candidates) < 3:
                candidates.extend(search_openverse_images(clean_api_q, max_results=4))
        else:
            candidates = search_bing_images(q_str, max_results=6, lang=lang, country=country)
            if len(candidates) < 2:
                candidates.extend(search_wikimedia_commons_images(q_str, max_results=4))
            if not candidates:
                candidates.extend(search_openverse_images(q_str, max_results=3))

        downloaded_for_query = 0
        for cand in candidates:
            if downloaded_for_query >= slot_cap or len(saved) >= max_images:
                break
            primary_u = cand.get("image_url") or ""
            thumb_u = cand.get("thumb_url") or ""
            if primary_u in seen_urls:
                continue

            engine = cand.get("source_engine") or "bing_images"
            active_sess = wiki_session if engine in ("wikimedia_commons", "openverse") else session
            raw_bytes: bytes | None = None
            final_url = ""
            last_err = ""
            for attempt_url in [u for u in (primary_u, thumb_u) if u]:
                if attempt_url in seen_urls:
                    continue
                # Respect robots.txt on arbitrary third-party hosts (official Wikimedia Commons API CDN is pre-authorized via User-Agent)
                attempt_host = (urlparse(attempt_url).hostname or "").lower()
                is_official_media_cdn = attempt_host.endswith("wikimedia.org")
                if respect_robots and not is_official_media_cdn:
                    if not is_url_allowed_by_robots(attempt_url, user_agent=str(active_sess.headers.get("User-Agent") or "*"), session=active_sess):
                        last_err = f"Disallowed by robots.txt: {attempt_host}"
                        logger.debug("Skipping %s (%s)", attempt_url, last_err)
                        # If the primary source host disallows crawling via robots.txt, do not bypass via cached thumbnail
                        break
                try:
                    raw_bytes, final_url = fetch_public_image_bytes(
                        active_sess,
                        attempt_url,
                        max_bytes=MAX_REFERENCE_IMAGE_BYTES,
                        timeout=DOWNLOAD_TIMEOUT_SEC,
                    )
                    break
                except Exception as exc:  # noqa: BLE001
                    last_err = str(exc)
                    continue

            if not raw_bytes:
                logger.debug("Reference image download skipped (%s): %s", label, last_err)
                continue

            next_num = len(saved) + 1
            cat_slug = slugify(category.replace("_", "-"), 16)
            lbl_slug = slugify(label, 28)
            stem = f"ref_{next_num:02d}_{cat_slug}_{lbl_slug}"

            try:
                out_path, w, h, fmt, size_bytes, dom_hex, fp = _save_verified_reference_image(
                    raw_bytes,
                    dest_dir=refs_dir,
                    stem=stem,
                    run_dir=run_dir,
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Reference image verify failed (%s): %s", label, exc)
                continue

            if fp in seen_fingerprints:
                try:
                    out_path.unlink(missing_ok=True)
                except OSError:
                    pass
                continue

            seen_fingerprints.add(fp)
            seen_urls.add(primary_u)
            if final_url:
                seen_urls.add(final_url)

            saved.append(DomainReferenceImage(
                evidence_id=f"EV-REF-{next_num:02d}",
                category=category,
                subject_label=label,
                query=q_str,
                title=cand.get("title") or label,
                source_engine=cand.get("source_engine") or "bing_images",
                source_url=final_url or primary_u,
                page_url=cand.get("page_url") or final_url or primary_u,
                domain=cand.get("domain") or (urlparse(final_url or primary_u).hostname or "").lower(),
                license_note=cand.get("license_note")
                or "Visual reference only (verify rights; do not copy trademarked logos or brand photography)",
                local_path=out_path.relative_to(run_dir).as_posix(),
                width=w,
                height=h,
                image_format=fmt,
                file_size_bytes=size_bytes,
                dominant_colors=dom_hex,
                downloaded=True,
            ))
            downloaded_for_query += 1

    # Compose visual moodboard sheet & real-world subject color palette card
    sheet_rel = build_domain_reference_sheet(
        saved,
        run_dir=run_dir,
        output_path=safe_join(refs_dir, "domain_reference_sheet.png"),
        subject_title=subject_title or "Domain Subject",
    )

    palette_swatches: list[ColorSwatch] = []
    palette_card_rel = ""
    imgs: list[Image.Image] = []
    try:
        for ref in saved[:16]:
            p = run_dir / ref.local_path
            if p.exists():
                try:
                    with Image.open(p) as im:
                        imgs.append(im.convert("RGB").copy())
                except Exception:  # noqa: BLE001
                    continue
        if imgs:
            palette_swatches = extract_palette_swatches(imgs, top_k=8)
            card_path = safe_join(refs_dir, "domain_palette_card.png")
            if render_palette_card(palette_swatches, f"Real-World Subject Palette: {subject_title or 'Domain'}", card_path):
                palette_card_rel = card_path.relative_to(run_dir).as_posix()
    finally:
        for im in imgs:
            im.close()

    return saved, sheet_rel, palette_swatches, palette_card_rel
