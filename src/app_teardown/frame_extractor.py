"""Hybrid FFmpeg scene-change + interval keyframe extractor, storyboards, and visual palette cards."""

from __future__ import annotations

import json
import logging
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .config import (
    DEFAULT_MAX_FRAMES,
    DEFAULT_MIN_FRAME_GAP_SEC,
    DEFAULT_SCENE_THRESHOLD,
)
from .models import ColorSwatch, KeyframeRecord, YouTubeVideoRecord
from .utils import format_timestamp_mmss, safe_join

logger = logging.getLogger(__name__)


def probe_video_metadata(video_path: Path) -> dict[str, Any]:
    """Probe resolution, duration, and FPS using ffprobe (shell=False)."""
    ffprobe_bin = shutil.which("ffprobe")
    if not ffprobe_bin or not video_path.exists():
        return {}
    try:
        proc = subprocess.run(
            [
                ffprobe_bin,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration",
                "-show_entries", "format=duration",
                "-of", "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
        if proc.returncode != 0:
            return {}
        data = json.loads(proc.stdout or "{}")
        streams = data.get("streams") or []
        stream = streams[0] if streams else {}
        fmt = data.get("format") or {}
        dur = float(stream.get("duration") or fmt.get("duration") or 0.0)
        fps_raw = str(stream.get("r_frame_rate") or "0/1")
        fps = 0.0
        if "/" in fps_raw:
            num, den = fps_raw.split("/", 1)
            if float(den) > 0:
                fps = round(float(num) / float(den), 2)
        return {
            "width": int(stream.get("width") or 0),
            "height": int(stream.get("height") or 0),
            "duration_sec": round(dur, 2),
            "fps": fps,
        }
    except Exception:  # noqa: BLE001
        return {}


def _detect_scene_timestamps(
    video_path: Path,
    threshold: float = DEFAULT_SCENE_THRESHOLD,
    max_candidates: int = 36,
) -> list[float]:
    """Detect major UI/screen transitions via FFmpeg scene-change filter."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin or not video_path.exists():
        return []
    try:
        proc = subprocess.run(
            [
                ffmpeg_bin,
                "-i", str(video_path),
                "-vf", f"select='gt(scene,{threshold:.2f})',showinfo",
                "-f", "null",
                "-",
            ],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        timestamps: list[float] = []
        for match in re.finditer(r"pts_time:(\d+(?:\.\d+)?)", proc.stderr or ""):
            ts = round(float(match.group(1)), 2)
            timestamps.append(ts)
            if len(timestamps) >= max_candidates * 2:
                break
        return timestamps
    except Exception as exc:  # noqa: BLE001
        logger.debug("Scene change detection skipped for %s: %s", video_path, exc)
        return []


def select_hybrid_timestamps(
    duration_sec: float,
    scene_timestamps: list[float],
    max_frames: int = DEFAULT_MAX_FRAMES,
    min_gap_sec: float = DEFAULT_MIN_FRAME_GAP_SEC,
) -> list[tuple[float, str]]:
    """Combine scene transitions and uniform interval anchors into a deduplicated timeline."""
    dur = max(duration_sec, 4.0)
    target = max(4, max_frames)
    adaptive_gap = min(min_gap_sec, max(1.0, dur / (target * 1.4)))

    chosen: list[tuple[float, str]] = []

    def _is_far_enough(t: float) -> bool:
        return all(abs(t - existing) >= adaptive_gap for existing, _ in chosen)

    # Always anchor near launch/FTUE start (1.5s)
    start_anchor = round(min(1.5, dur * 0.05), 2)
    chosen.append((start_anchor, "interval"))

    # Add up to 60% of budget from detected UI/scene transitions
    scene_budget = max(2, int(target * 0.6))
    for ts in sorted(scene_timestamps):
        if len(chosen) >= scene_budget + 1:
            break
        if 0.5 <= ts <= max(0.6, dur - 0.5) and _is_far_enough(ts):
            chosen.append((round(ts, 2), "scene_change"))

    # Fill remaining slots uniformly across the clip to guarantee full phase coverage
    if len(chosen) < target:
        step = dur / float(target + 1)
        for i in range(1, target + 2):
            if len(chosen) >= target:
                break
            ts = round(min(dur - 0.4, i * step), 2)
            if ts >= 0.2 and _is_far_enough(ts):
                chosen.append((ts, "interval"))

    # If still short (e.g., short clip), relax gap slightly
    if len(chosen) < min(target, int(dur)):
        step = dur / float(target)
        for i in range(target):
            if len(chosen) >= target:
                break
            ts = round(min(dur - 0.2, i * step + 0.2), 2)
            if all(abs(ts - ex) >= 0.7 for ex, _ in chosen):
                chosen.append((ts, "interval"))

    chosen.sort(key=lambda x: x[0])
    return chosen[:target]


def _phase_hint_for_timestamp(ts: float, duration_sec: float) -> str:
    dur = max(duration_sec, 1.0)
    ratio = ts / dur
    if ts <= 35.0 or ratio <= 0.18:
        return "ftue_launch"
    if ratio <= 0.48:
        return "early_core"
    if ratio <= 0.78:
        return "mid_loop"
    return "late_monetization_meta"


def _classify_color_temperature(r: int, g: int, b: int) -> str:
    if max(r, g, b) - min(r, g, b) < 22:
        return "neutral"
    if r >= b + 18:
        return "warm"
    if b >= r + 18:
        return "cool"
    return "neutral"


def load_ui_font(size: int = 14) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a clean Unicode-capable system TTF font (supporting Turkish & symbols), with safe default fallback."""
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for fp in candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def extract_palette_swatches(images: list[Image.Image], top_k: int = 8) -> list[ColorSwatch]:
    """Extract aggregated dominant color swatches across one or more PIL images without black-padding bias."""
    if not images:
        return []
    # Fit each image tightly into 96x96 and pack into a 1-row strip (zero empty cells, zero letterbox padding)
    thumbs: list[Image.Image] = []
    for im in images[:16]:
        rgb = im.convert("RGB")
        fitted = ImageOps.fit(rgb, (96, 96), method=Image.Resampling.BILINEAR)
        thumbs.append(fitted)
    mosaic = Image.new("RGB", (len(thumbs) * 96, 96))
    for i, th in enumerate(thumbs):
        mosaic.paste(th, (i * 96, 0))

    quantized = mosaic.quantize(colors=top_k, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = sorted(quantized.getcolors() or [], key=lambda x: x[0], reverse=True)
    total_px = sum(cnt for cnt, _ in counts) or 1

    swatches: list[ColorSwatch] = []
    seen_hex: set[str] = set()
    for cnt, idx in counts[:top_k]:
        base = idx * 3
        if base + 2 >= len(palette):
            continue
        r, g, b = int(palette[base]), int(palette[base + 1]), int(palette[base + 2])
        hx = f"#{r:02X}{g:02X}{b:02X}"
        if hx in seen_hex:
            continue
        seen_hex.add(hx)
        lum = round((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0, 3)
        swatches.append(ColorSwatch(
            hex=hx,
            rgb=(r, g, b),
            ratio_pct=round((cnt / total_px) * 100.0, 1),
            luminance=lum,
            temperature=_classify_color_temperature(r, g, b),
        ))
    return swatches


def render_palette_card(swatches: list[ColorSwatch], title: str, output_path: Path) -> bool:
    """Render a crisp visual HEX color palette swatch card for reports and multimodal inspection."""
    if not swatches:
        return False
    try:
        n = len(swatches)
        card_w = max(720, n * 124 + 40)
        card_h = 216
        img = Image.new("RGB", (card_w, card_h), (15, 20, 30))
        draw = ImageDraw.Draw(img)
        title_font = load_ui_font(16)
        hex_font = load_ui_font(14)
        meta_font = load_ui_font(12)
        draw.text((20, 14), f"Color Palette Analysis - {title[:64]}", fill=(240, 245, 255), font=title_font)

        box_w = (card_w - 40 - (n - 1) * 10) // n
        for i, sw in enumerate(swatches):
            x0 = 20 + i * (box_w + 10)
            y0 = 48
            y1 = 150
            draw.rectangle([x0, y0, x0 + box_w, y1], fill=sw.rgb, outline=(70, 82, 104), width=1)
            draw.text((x0 + 4, y1 + 8), sw.hex, fill=(240, 245, 255), font=hex_font)
            draw.text((x0 + 4, y1 + 28), f"{sw.ratio_pct:.1f}% | {sw.temperature}", fill=(156, 168, 188), font=meta_font)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, format="PNG", optimize=True)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.debug("Palette card rendering failed: %s", exc)
        return False


def _build_storyboard_grids(
    frames: list[KeyframeRecord],
    app_dir: Path,
    frames_dir: Path,
    stem: str,
    tiles_per_sheet: int = 12,
) -> list[str]:
    """Compose 3x4 timestamped, phase-labeled storyboard PNG sheets for rapid multimodal review."""
    valid = [f for f in frames if f.local_path and (app_dir / f.local_path).exists()]
    if not valid:
        return []

    first_path = app_dir / valid[0].local_path
    with Image.open(first_path) as first_im:
        fw, fh = first_im.size
    is_landscape = fw >= fh
    tile_w, tile_h = (384, 216) if is_landscape else (225, 400)
    header_h = 30
    pad = 12
    cols = 3 if is_landscape else 4

    phase_colors = {
        "ftue_launch": (30, 64, 110),
        "early_core": (26, 86, 72),
        "mid_loop": (88, 62, 24),
        "late_monetization_meta": (96, 36, 68),
    }

    sheet_paths: list[str] = []
    total_sheets = math.ceil(len(valid) / tiles_per_sheet)
    for sheet_idx in range(total_sheets):
        chunk = valid[sheet_idx * tiles_per_sheet : (sheet_idx + 1) * tiles_per_sheet]
        rows = math.ceil(len(chunk) / cols)
        canvas = Image.new(
            "RGB",
            (pad + cols * (tile_w + pad), pad + rows * (tile_h + header_h + pad)),
            (13, 17, 23),
        )
        draw = ImageDraw.Draw(canvas)
        for pos, kf in enumerate(chunk):
            r, c = divmod(pos, cols)
            x0 = pad + c * (tile_w + pad)
            y0 = pad + r * (tile_h + header_h + pad)
            hdr_bg = phase_colors.get(kf.phase_hint, (38, 48, 66))
            tag = "SCN" if kf.source == "scene_change" else "TIM"
            label = f"#{kf.index:02d} @{kf.timestamp_label} [{tag}]"
            draw.rectangle([x0, y0, x0 + tile_w, y0 + header_h - 2], fill=hdr_bg)
            draw.text((x0 + 8, y0 + 7), label, fill=(242, 246, 255))
            with Image.open(app_dir / kf.local_path) as im:
                thumb = ImageOps.contain(im.convert("RGB"), (tile_w, tile_h))
                canvas.paste(
                    thumb,
                    (x0 + (tile_w - thumb.width) // 2, y0 + header_h + (tile_h - thumb.height) // 2),
                )
        out_name = f"{stem}_storyboard_{sheet_idx + 1:02d}.png"
        out_path = safe_join(frames_dir, out_name)
        canvas.save(out_path, format="PNG", optimize=True)
        sheet_paths.append(out_path.relative_to(app_dir).as_posix())
    return sheet_paths


def extract_frames_and_palette(
    video: YouTubeVideoRecord,
    video_path: Path,
    frames_dir: Path,
    app_dir: Path,
    stem: str = "gameplay_01",
    max_frames: int = DEFAULT_MAX_FRAMES,
    scene_threshold: float = DEFAULT_SCENE_THRESHOLD,
) -> YouTubeVideoRecord:
    """Run hybrid scene-change + interval extraction, storyboards, and palette card generation."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin or not video_path.exists():
        if not ffmpeg_bin:
            video.error = (video.error + "; " if video.error else "") + "ffmpeg not found in PATH"
        return video

    probe = probe_video_metadata(video_path)
    video.width = probe.get("width", video.width)
    video.height = probe.get("height", video.height)
    video.clip_duration_sec = probe.get("duration_sec", video.duration_sec or 0.0)
    video.fps = probe.get("fps", 0.0)

    dur = video.clip_duration_sec if video.clip_duration_sec > 0 else 60.0
    scene_ts = _detect_scene_timestamps(video_path, threshold=scene_threshold, max_candidates=max_frames)
    selected = select_hybrid_timestamps(dur, scene_ts, max_frames=max_frames)

    frames_dir.mkdir(parents=True, exist_ok=True)
    keyframes: list[KeyframeRecord] = []
    opened_for_palette: list[Image.Image] = []

    for idx, (ts, src_kind) in enumerate(selected, start=1):
        mmss = format_timestamp_mmss(ts)
        fname = f"{stem}_frame_{idx:02d}_{mmss.replace(':', 'm')}s.jpg"
        out_frame = safe_join(frames_dir, fname)
        proc = subprocess.run(
            [
                ffmpeg_bin,
                "-y",
                "-ss", f"{ts:.2f}",
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "3",
                str(out_frame),
            ],
            capture_output=True,
            timeout=25,
            check=False,
        )
        if proc.returncode != 0 or not out_frame.exists() or out_frame.stat().st_size == 0:
            continue

        try:
            with Image.open(out_frame) as im:
                rgb = im.convert("RGB")
                fw, fh = rgb.size
                swatches = extract_palette_swatches([rgb], top_k=4)
                # Compute average perceptual brightness (0-1)
                small = rgb.resize((32, 32))
                pixels = list(small.getdata())
                avg_lum = sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels) / (len(pixels) * 255.0)
                if len(opened_for_palette) < 16:
                    opened_for_palette.append(rgb.copy())
            keyframes.append(KeyframeRecord(
                index=len(keyframes) + 1,
                timestamp_sec=ts,
                timestamp_label=mmss,
                source=src_kind,
                phase_hint=_phase_hint_for_timestamp(ts, dur),
                local_path=out_frame.relative_to(app_dir).as_posix(),
                width=fw,
                height=fh,
                dominant_colors=[s.hex for s in swatches],
                avg_brightness=round(avg_lum, 3),
            ))
        except Exception as exc:  # noqa: BLE001
            logger.debug("Frame inspect error on %s: %s", out_frame, exc)

    video.frames = keyframes
    video.storyboard_paths = _build_storyboard_grids(keyframes, app_dir, frames_dir, stem=stem)

    if opened_for_palette:
        agg_swatches = extract_palette_swatches(opened_for_palette, top_k=8)
        video.dominant_colors = agg_swatches
        card_path = safe_join(frames_dir, f"{stem}_palette_card.png")
        if render_palette_card(agg_swatches, video.title or stem, card_path):
            video.palette_card_path = card_path.relative_to(app_dir).as_posix()
        for im in opened_for_palette:
            im.close()

    return video
