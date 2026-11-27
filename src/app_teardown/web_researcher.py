"""Zero-API-key web evidence harvester (DuckDuckGo HTML) for revenue, monetization, and UX teardowns."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, unquote, urlparse

from bs4 import BeautifulSoup

from .config import REQUEST_TIMEOUT_SEC
from .models import WebEvidenceItem
from .utils import create_http_session, sanitize_untrusted_text, validate_public_web_url

logger = logging.getLogger(__name__)


def build_web_research_queries(app_title: str, product_mode: str = "game", developer: str = "") -> list[tuple[str, str]]:
    """Build categorized web research queries for monetization, retention, revenue, and UX teardowns."""
    name = (app_title or "").strip()
    dev = (developer or "").strip()
    if product_mode == "game":
        return [
            ("revenue_downloads", f'"{name}" mobile game revenue downloads sensor tower OR appmagic'),
            ("monetization_ads", f'"{name}" monetization strategy IAP rewarded ads interstitial'),
            ("gameplay_design", f'"{name}" game design teardown core loop retention'),
            ("retention_ux", f'"{name}" {dev} player retention live ops meta progression'.strip()),
        ]
    return [
        ("revenue_downloads", f'"{name}" app revenue downloads ARR users'),
        ("monetization_ads", f'"{name}" paywall pricing subscription monetization strategy'),
        ("retention_ux", f'"{name}" onboarding UX teardown retention growth loop'),
    ]


def _decode_ddg_redirect(raw_href: str) -> str:
    """Resolve DuckDuckGo /l/?uddg=... redirect URLs into real destination URLs."""
    if not raw_href:
        return ""
    href = raw_href.strip()
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if "duckduckgo.com" in (parsed.hostname or "") and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        uddg = (qs.get("uddg") or [""])[0]
        if uddg:
            return unquote(uddg)
    return href


def search_duckduckgo_html(
    query: str,
    max_results: int = 5,
    lang: str = "en",
    country: str = "us",
) -> list[dict[str, str]]:
    """Fetch search snippets from DuckDuckGo's public HTML interface without API keys."""
    session = create_http_session(lang=lang, country=country)
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = session.post(
            url,
            data={"q": query, "kl": f"{country.lower()}-{lang.lower()}"},
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results: list[dict[str, str]] = []
        for card in soup.select(".result"):
            a = card.select_one("a.result__a")
            if not a:
                continue
            raw_href = a.get("href") or ""
            resolved = _decode_ddg_redirect(str(raw_href))
            try:
                safe_url = validate_public_web_url(resolved)
            except ValueError:
                continue
            title = sanitize_untrusted_text(a.get_text(" ", strip=True), max_len=240)
            snip_el = card.select_one(".result__snippet")
            snippet = sanitize_untrusted_text(snip_el.get_text(" ", strip=True) if snip_el else "", max_len=500)
            domain = (urlparse(safe_url).hostname or "").lower()
            results.append({
                "title": title,
                "url": safe_url,
                "domain": domain,
                "snippet": snippet,
            })
            if len(results) >= max_results:
                break
        return results
    except Exception as exc:  # noqa: BLE001
        logger.debug("DuckDuckGo HTML search failed for %r: %s", query, exc)
        return []


def collect_competitor_web_evidence(
    app_title: str,
    product_mode: str = "game",
    developer: str = "",
    lang: str = "en",
    country: str = "us",
    max_per_query: int = 3,
    polite_delay_sec: float = 0.6,
) -> list[WebEvidenceItem]:
    """Run categorized web searches and return deduplicated, URL-verified evidence records."""
    queries = build_web_research_queries(app_title, product_mode=product_mode, developer=developer)
    items: list[WebEvidenceItem] = []
    seen_urls: set[str] = set()
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    for idx, (category, q) in enumerate(queries):
        if idx > 0 and polite_delay_sec > 0:
            time.sleep(polite_delay_sec)
        hits = search_duckduckgo_html(q, max_results=max_per_query, lang=lang, country=country)
        for hit in hits:
            u = hit["url"]
            if u in seen_urls:
                continue
            seen_urls.add(u)
            items.append(WebEvidenceItem(
                evidence_id=f"EV-WEB-{len(items) + 1:02d}",
                category=category,
                query=q,
                title=hit["title"],
                url=u,
                domain=hit["domain"],
                snippet=hit["snippet"],
                fetched_at=now_iso,
            ))
    return items
