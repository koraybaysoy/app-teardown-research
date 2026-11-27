"""YouTube gameplay & app walkthrough discovery and bounded-clip downloader via yt-dlp."""

from __future__ import annotations

import logging
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    DEFAULT_MAX_VIDEO_SEC,
    MAX_VIDEO_BYTES,
    VIDEO_TIMEOUT_SEC,
)
from .models import YouTubeVideoRecord
from .utils import safe_join, validate_asset_url

logger = logging.getLogger(__name__)


def build_youtube_queries(app_title: str, product_mode: str = "game", developer: str = "") -> list[str]:
    """Generate prioritized YouTube search queries tailored for games vs general apps."""
    clean_title = re.sub(r"[:\-–|()\[\]]+", " ", app_title or "").strip()
    short_title = " ".join(clean_title.split()[:5])
    if product_mode == "game":
        return [
            f'"{short_title}" gameplay no commentary mobile',
            f"{short_title} mobile gameplay walkthrough iOS Android",
            f"{short_title} gameplay first 10 minutes",
        ]
    return [
        f'"{short_title}" app walkthrough UI tour',
        f"{short_title} app tutorial review onboarding",
        f"{short_title} mobile app demo",
    ]


def score_youtube_candidate(
    entry: dict[str, Any],
    app_title: str,
    product_mode: str = "game",
) -> float:
    """Score a YouTube search candidate for clean gameplay/walkthrough suitability."""
    title = str(entry.get("title") or "").lower()
    duration = float(entry.get("duration") or 0.0)
    views = int(entry.get("view_count") or 0)
    is_live = bool(entry.get("is_live") or entry.get("live_status") == "is_live")

    if is_live:
        return -100.0
    if duration and duration < 25:
        return -40.0

    score = 0.0
    # Token overlap with target app title
    app_tokens = [t for t in re.findall(r"[a-z0-9]{2,}", app_title.lower()) if t not in ("the", "and", "app", "game", "pro")]
    if app_tokens:
        matched = sum(1 for tok in app_tokens if tok in title)
        score += (matched / len(app_tokens)) * 45.0

    if product_mode == "game":
        for kw, pts in (
            ("no commentary", 22.0),
            ("gameplay", 18.0),
            ("walkthrough", 14.0),
            ("ios", 8.0),
            ("android", 8.0),
            ("mobile", 8.0),
            ("level 1", 8.0),
            ("first look", 6.0),
        ):
            if kw in title:
                score += pts
        for bad, pen in (
            ("#shorts", -25.0),
            ("shorts", -15.0),
            ("mod apk", -35.0),
            ("hack", -35.0),
            ("cheat", -30.0),
            ("trailer only", -10.0),
            ("reaction", -12.0),
        ):
            if bad in title:
                score += pen
    else:
        for kw, pts in (
            ("walkthrough", 20.0),
            ("tour", 16.0),
            ("review", 14.0),
            ("tutorial", 14.0),
            ("onboarding", 15.0),
            ("ui", 10.0),
            ("demo", 12.0),
            ("how to use", 12.0),
        ):
            if kw in title:
                score += pts
        for bad, pen in (
            ("#shorts", -22.0),
            ("cracked", -35.0),
            ("mod apk", -35.0),
            ("scam", -10.0),
        ):
            if bad in title:
                score += pen

    # Ideal duration window: 1.5 min to 18 min (captures launch -> loop -> monetization)
    if 90 <= duration <= 1080:
        score += 18.0
    elif 40 <= duration < 90:
        score += 8.0
    elif 1080 < duration <= 2700:
        score += 5.0
    elif duration > 2700:
        score -= 10.0

    if views > 0:
        score += min(15.0, math.log10(views + 1) * 2.5)

    return round(score, 2)


def search_youtube_gameplay(
    app_title: str,
    product_mode: str = "game",
    developer: str = "",
    max_candidates: int = 8,
) -> list[YouTubeVideoRecord]:
    """Search YouTube via yt-dlp flat extraction (no download) and return ranked candidates."""
    import yt_dlp

    queries = build_youtube_queries(app_title, product_mode=product_mode, developer=developer)
    seen_ids: set[str] = set()
    scored: list[YouTubeVideoRecord] = []

    ydl_opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "socket_timeout": 20,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for q in queries[:2]:
            try:
                info = ydl.extract_info(f"ytsearch{max_candidates}:{q}", download=False)
                entries = (info or {}).get("entries") or []
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    vid = str(entry.get("id") or "").strip()
                    if not vid or vid in seen_ids:
                        continue
                    seen_ids.add(vid)
                    url = entry.get("url") or f"https://www.youtube.com/watch?v={vid}"
                    if not str(url).startswith("http"):
                        url = f"https://www.youtube.com/watch?v={vid}"
                    sel_score = score_youtube_candidate(entry, app_title, product_mode=product_mode)
                    scored.append(YouTubeVideoRecord(
                        video_id=vid,
                        title=str(entry.get("title") or "").strip(),
                        channel=str(entry.get("channel") or entry.get("uploader") or "").strip(),
                        duration_sec=float(entry.get("duration") or 0.0),
                        view_count=int(entry.get("view_count") or 0),
                        upload_date=str(entry.get("upload_date") or ""),
                        url=url,
                        search_query=q,
                        selection_score=sel_score,
                    ))
            except Exception as exc:  # noqa: BLE001
                logger.warning("YouTube search failed for query %r: %s", q, exc)
            if len(scored) >= max_candidates:
                break

    scored.sort(key=lambda r: r.selection_score, reverse=True)
    return scored[:max_candidates]


def _trim_video_if_needed(video_path: Path, max_video_sec: int) -> Path:
    """Trim video to max_video_sec using ffmpeg stream copy (no shell) if longer than cap."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin or max_video_sec <= 0 or not video_path.exists():
        return video_path
    trimmed = video_path.with_name(video_path.stem + "_clip.mp4")
    proc = subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-ss", "0",
            "-t", str(int(max_video_sec)),
            "-i", str(video_path),
            "-c", "copy",
            "-movflags", "+faststart",
            str(trimmed),
        ],
        capture_output=True,
        timeout=VIDEO_TIMEOUT_SEC,
        check=False,
    )
    if proc.returncode == 0 and trimmed.exists() and trimmed.stat().st_size > 0:
        try:
            video_path.unlink(missing_ok=True)
            trimmed.rename(video_path)
        except OSError:
            return trimmed
    else:
        trimmed.unlink(missing_ok=True)
    return video_path


def download_youtube_clip(
    video: YouTubeVideoRecord,
    videos_dir: Path,
    app_dir: Path,
    stem: str = "gameplay_01",
    max_video_sec: int = DEFAULT_MAX_VIDEO_SEC,
) -> YouTubeVideoRecord:
    """Download a bounded clip (first max_video_sec seconds) from YouTube safely via yt-dlp."""
    import yt_dlp
    from yt_dlp.utils import download_range_func

    try:
        safe_url = validate_asset_url(video.url)
        videos_dir.mkdir(parents=True, exist_ok=True)
        out_template = str(safe_join(videos_dir, f"{stem}.%(ext)s"))
        expected_mp4 = safe_join(videos_dir, f"{stem}.mp4")

        base_opts: dict[str, Any] = {
            "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
            "merge_output_format": "mp4",
            "outtmpl": out_template,
            "max_filesize": MAX_VIDEO_BYTES,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 30,
        }

        downloaded_ok = False
        if max_video_sec > 0 and shutil.which("ffmpeg"):
            range_opts = dict(base_opts)
            range_opts["download_ranges"] = download_range_func(None, [(0, max_video_sec)])
            range_opts["force_keyframes_at_cuts"] = False
            try:
                with yt_dlp.YoutubeDL(range_opts) as ydl:
                    info = ydl.extract_info(safe_url, download=True)
                    if isinstance(info, dict):
                        video.title = video.title or str(info.get("title") or "")
                        video.channel = video.channel or str(info.get("channel") or info.get("uploader") or "")
                        video.duration_sec = float(info.get("duration") or video.duration_sec or 0.0)
                        video.view_count = int(info.get("view_count") or video.view_count or 0)
                        video.video_id = video.video_id or str(info.get("id") or "")
                downloaded_ok = True
            except Exception as range_exc:  # noqa: BLE001
                logger.debug("Range download fallback for %s: %s", safe_url, range_exc)

        if not downloaded_ok:
            with yt_dlp.YoutubeDL(base_opts) as ydl:
                info = ydl.extract_info(safe_url, download=True)
                if isinstance(info, dict):
                    video.title = video.title or str(info.get("title") or "")
                    video.channel = video.channel or str(info.get("channel") or info.get("uploader") or "")
                    video.duration_sec = float(info.get("duration") or video.duration_sec or 0.0)
                    video.view_count = int(info.get("view_count") or video.view_count or 0)
                    video.video_id = video.video_id or str(info.get("id") or "")

        out_file = expected_mp4
        if not out_file.exists():
            for cand in videos_dir.glob(f"{stem}.*"):
                if cand.suffix.lower() in (".mp4", ".mkv", ".webm", ".mov"):
                    out_file = cand
                    break

        if not out_file.exists() or out_file.stat().st_size == 0:
            raise RuntimeError("Downloaded YouTube video file is missing or empty")

        if max_video_sec > 0 and video.duration_sec > max_video_sec + 15:
            out_file = _trim_video_if_needed(out_file, max_video_sec)

        video.file_size_bytes = out_file.stat().st_size
        video.local_path = out_file.relative_to(app_dir).as_posix()
        video.downloaded = True
    except Exception as exc:  # noqa: BLE001
        video.error = str(exc)
        logger.warning("YouTube clip download failed (%s): %s", video.url, exc)
    return video
