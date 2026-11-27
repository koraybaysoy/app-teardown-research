"""Security-first utilities: path guards, SSRF URL validation, HTTP client, and parsers."""

from __future__ import annotations

import ipaddress
import os
import re
import socket
import unicodedata
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    ALLOWED_ASSET_HOST_SUFFIXES,
    DEFAULT_USER_AGENT,
    DOWNLOAD_TIMEOUT_SEC,
    MAX_REFERENCE_IMAGE_BYTES,
    REQUEST_TIMEOUT_SEC,
)

_DISALLOWED_IMAGE_EXTENSIONS = (
    ".svg", ".svgz", ".ico", ".html", ".htm", ".php", ".js", ".css", ".xml", ".pdf", ".zip", ".mp4",
)

_WINDOWS_RESERVED_NAMES = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
})


def slugify(value: str, max_len: int = 48) -> str:
    """Convert arbitrary text into a strictly safe ASCII filesystem slug."""
    if not isinstance(value, str):
        return "item"
    normalized = unicodedata.normalize("NFKD", value)
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    cleaned = normalized.translate(tr_map).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", cleaned.lower()).strip("-")
    cleaned = cleaned[:max_len].strip("-")
    if not cleaned or cleaned in _WINDOWS_RESERVED_NAMES:
        return "app-item"
    return cleaned


def safe_join(base_dir: Path, *parts: str) -> Path:
    """Join path segments under base_dir and strictly block path traversal."""
    base_resolved = base_dir.resolve()
    sanitized_parts: list[str] = []
    for part in parts:
        if not part or part in (".", "..") or "\x00" in part:
            raise ValueError(f"Invalid path segment: {part!r}")
        if os.path.isabs(part) or "/" in part or "\\" in part:
            raise ValueError(f"Path segment must not contain separators: {part!r}")
        sanitized_parts.append(part)
    candidate = base_resolved.joinpath(*sanitized_parts).resolve()
    base_prefix = str(base_resolved) + os.sep
    if candidate != base_resolved and not str(candidate).startswith(base_prefix):
        raise ValueError(f"Path traversal blocked: {candidate} escapes {base_resolved}")
    return candidate


def _reject_unsafe_host(host: str) -> None:
    if not host:
        raise ValueError("Missing hostname in URL")
    if host in ("localhost", "localhost.localdomain") or host.endswith(".local") or host.endswith(".internal"):
        raise ValueError(f"Local/internal host is not allowed: {host}")
    try:
        ip_obj = ipaddress.ip_address(host)
        raise ValueError(f"Direct IP URLs are not allowed: {ip_obj}")
    except ValueError as exc:
        if "Direct IP URLs" in str(exc):
            raise


def validate_asset_url(url: str) -> str:
    """Validate an asset, store, or YouTube URL against scheme, IP, and CDN allowlist."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Empty URL")
    trimmed = url.strip()
    parsed = urlparse(trimmed)
    if parsed.scheme not in ("https", "http"):
        raise ValueError(f"Disallowed URL scheme: {parsed.scheme!r}")
    if parsed.scheme == "http":
        trimmed = "https://" + trimmed[len("http://"):]
        parsed = urlparse(trimmed)
    host = (parsed.hostname or "").lower().strip(".")
    _reject_unsafe_host(host)
    allowed = any(
        host == suffix or host.endswith("." + suffix)
        for suffix in ALLOWED_ASSET_HOST_SUFFIXES
    )
    if not allowed:
        raise ValueError(f"Host {host!r} is not in the store/CDN allowlist")
    return trimmed


def validate_public_web_url(url: str) -> str:
    """Validate a public web citation URL (HTTPS/HTTP, no IPs, no local/internal hosts)."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Empty URL")
    trimmed = url.strip()
    parsed = urlparse(trimmed)
    if parsed.scheme not in ("https", "http"):
        raise ValueError(f"Disallowed URL scheme: {parsed.scheme!r}")
    host = (parsed.hostname or "").lower().strip(".")
    _reject_unsafe_host(host)
    if "." not in host:
        raise ValueError(f"Non-public hostname rejected: {host}")
    return trimmed


def validate_public_image_url(url: str, resolve_dns: bool = True) -> str:
    """Validate a public web image URL with SSRF defense (global-IP DNS check + non-SVG guard)."""
    safe_url = validate_public_web_url(url)
    parsed = urlparse(safe_url)
    path_low = (parsed.path or "").lower()
    if any(path_low.endswith(ext) for ext in _DISALLOWED_IMAGE_EXTENSIONS):
        raise ValueError(f"Disallowed image extension in URL: {parsed.path}")
    if resolve_dns:
        host = (parsed.hostname or "").lower().strip(".")
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError(f"DNS resolution failed for host {host!r}: {exc}") from exc
        if not infos:
            raise ValueError(f"No IP addresses resolved for host {host!r}")
        for info in infos:
            ip_str = info[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if not ip_obj.is_global:
                raise ValueError(f"Non-global IP blocked for host {host!r}: {ip_str}")
    return safe_url


def fetch_public_image_bytes(
    session: requests.Session,
    url: str,
    max_bytes: int = MAX_REFERENCE_IMAGE_BYTES,
    timeout: int = DOWNLOAD_TIMEOUT_SEC,
    max_redirects: int = 3,
) -> tuple[bytes, str]:
    """Download public web image bytes with per-hop SSRF DNS validation and size/type caps."""
    current_url = url
    for _ in range(max_redirects + 1):
        safe_url = validate_public_image_url(current_url, resolve_dns=True)
        resp = session.get(safe_url, stream=True, timeout=timeout, allow_redirects=False)
        try:
            if resp.status_code in (301, 302, 303, 307, 308):
                loc = (resp.headers.get("Location") or "").strip()
                if not loc:
                    raise ValueError("Redirect without Location header")
                current_url = urljoin(safe_url, loc)
                continue
            resp.raise_for_status()
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if any(bad in ctype for bad in ("svg", "text/html", "javascript", "text/plain", "application/json", "xml")):
                raise ValueError(f"Rejected non-raster Content-Type: {ctype}")
            chunks: list[bytes] = []
            total = 0
            for chunk in resp.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"Reference image exceeds max size cap ({max_bytes} bytes)")
                chunks.append(chunk)
            raw = b"".join(chunks)
            if not raw:
                raise ValueError("Empty image response")
            return raw, safe_url
        finally:
            resp.close()
    raise ValueError(f"Too many redirects while fetching {url}")


def create_http_session(lang: str = "en", country: str = "us") -> requests.Session:
    """Create a resilient requests.Session with retries and clean headers."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=12, pool_maxsize=12)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept-Language": f"{lang}-{country.upper()},{lang};q=0.9,en;q=0.8",
    })
    return session


def http_get_json(
    session: requests.Session,
    url: str,
    params: dict[str, str | int] | None = None,
    timeout: int = REQUEST_TIMEOUT_SEC,
) -> dict:
    """Perform an HTTPS GET to an allowlisted host and decode JSON safely."""
    safe_url = validate_asset_url(url)
    resp = session.get(safe_url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_store_target(
    raw: str,
) -> tuple[Literal["google_play", "apple_app_store", "query"], str, str | None]:
    """Classify a target string into (kind, identifier, optional_country)."""
    text = raw.strip()
    if text.startswith(("http://", "https://")):
        parsed = urlparse(text)
        host = (parsed.hostname or "").lower()
        if "play.google.com" in host:
            qs = parse_qs(parsed.query)
            app_id = (qs.get("id") or [""])[0].strip()
            gl = (qs.get("gl") or [None])[0]
            if app_id:
                return ("google_play", app_id, gl.lower() if gl else None)
        if "apps.apple.com" in host or "itunes.apple.com" in host:
            m_id = re.search(r"/id(\d+)", parsed.path)
            m_country = re.match(r"^/([a-zA-Z]{2})/app/", parsed.path)
            if m_id:
                country = m_country.group(1).lower() if m_country else None
                return ("apple_app_store", m_id.group(1), country)
    m_apple = re.fullmatch(r"(?:id)?(\d{7,12})", text, flags=re.IGNORECASE)
    if m_apple:
        return ("apple_app_store", m_apple.group(1), None)
    if re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+){1,}", text):
        return ("google_play", text, None)
    return ("query", text, None)


def format_bytes(num_bytes: int) -> str:
    """Human-readable byte formatter."""
    if num_bytes <= 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB")
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{num_bytes} B"


def format_timestamp_mmss(seconds: float) -> str:
    """Format seconds into MM:SS label."""
    sec_int = max(0, int(round(seconds)))
    mins, secs = divmod(sec_int, 60)
    return f"{mins:02d}:{secs:02d}"


def parse_price_float(price_str: str) -> float | None:
    """Extract numeric price value from formatted currency strings like '$4.99' or 'TRY 149,99'."""
    if not price_str or not isinstance(price_str, str):
        return None
    m = re.search(r"(\d[\d.,]*)", price_str)
    if not m:
        return None
    raw = m.group(1)
    # Normalize European comma decimals like '4,99' vs thousands '1,299.99'
    if "," in raw and "." in raw:
        raw = raw.replace(",", "")
    elif "," in raw:
        parts = raw.split(",")
        raw = raw.replace(",", ".") if len(parts[-1]) == 2 else raw.replace(",", "")
    try:
        return round(float(raw), 2)
    except ValueError:
        return None


def parse_installs_int(installs_str: str) -> int:
    """Parse Google Play installs strings like '50,000,000+' into integers."""
    if not installs_str or not isinstance(installs_str, str):
        return 0
    digits = re.sub(r"\D+", "", installs_str)
    return int(digits) if digits else 0


def sanitize_untrusted_text(text: str, max_len: int = 2000) -> str:
    """Strip control characters and bound untrusted scraped text length."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text).strip()
    if len(cleaned) > max_len:
        return cleaned[:max_len].rstrip() + "..."
    return cleaned
