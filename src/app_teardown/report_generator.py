"""Evidence-backed Markdown & JSON report generators for per-app teardowns, domain research, free kits, and buildable blueprints."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .idea_planner import get_tech_profile
from .models import CompetitorRecord, TeardownRun
from .utils import format_bytes, safe_join, sanitize_untrusted_text


def build_evidence_ledger(record: CompetitorRecord) -> dict[str, Any]:
    """Create a complete machine-readable Evidence Ledger mapping every claimable artifact to an ID."""
    entries: list[dict[str, Any]] = [
        {
            "evidence_id": "EV-STORE-01",
            "type": "store_listing",
            "store": record.store,
            "url": record.store_url,
            "local_path": "store_metadata.md",
            "summary": f"{record.title} ({record.rating}★, {record.ratings_count} ratings, installs={record.installs or 'N/A'})",
        }
    ]
    if record.screenshots_sheet_path:
        entries.append({
            "evidence_id": "EV-SHOTS-01",
            "type": "store_screenshots_sheet",
            "local_path": record.screenshots_sheet_path,
            "count": len(record.screenshots),
        })
    if record.palette_card_path:
        entries.append({
            "evidence_id": "EV-PALETTE-01",
            "type": "color_palette_card",
            "local_path": record.palette_card_path,
            "hex_swatches": [s.hex for s in record.combined_palette],
        })
    for v_idx, vid in enumerate(record.youtube_videos, start=1):
        entries.append({
            "evidence_id": f"EV-VID-{v_idx:02d}",
            "type": "youtube_gameplay_video",
            "title": vid.title,
            "channel": vid.channel,
            "url": vid.url,
            "local_path": vid.local_path,
            "clip_duration_sec": vid.clip_duration_sec,
            "storyboards": vid.storyboard_paths,
            "frame_count": len(vid.frames),
        })
        for kf in vid.frames:
            entries.append({
                "evidence_id": f"EV-FRAME-{v_idx:02d}-{kf.index:02d}",
                "type": "video_keyframe",
                "timestamp": kf.timestamp_label,
                "source": kf.source,
                "phase": kf.phase_hint,
                "local_path": kf.local_path,
                "dominant_colors": kf.dominant_colors,
            })
    for w in record.web_evidence:
        entries.append({
            "evidence_id": w.evidence_id,
            "type": "web_source",
            "category": w.category,
            "title": w.title,
            "domain": w.domain,
            "url": w.url,
            "snippet": w.snippet,
        })
    return {
        "app_id": record.app_id,
        "store": record.store,
        "title": record.title,
        "product_mode": record.product_mode,
        "evidence_count": len(entries),
        "evidence_score": record.signals.evidence_score,
        "items": entries,
    }


def write_competitor_artifacts(record: CompetitorRecord, app_dir: Path) -> None:
    """Write store_metadata.md, web_research.md, evidence.json, metadata.json, and teardown_report.md."""
    app_dir.mkdir(parents=True, exist_ok=True)
    sig = record.signals

    safe_join(app_dir, "metadata.json").write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    ledger = build_evidence_ledger(record)
    safe_join(app_dir, "evidence.json").write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    iap_lines = [f"- **{i.name}** | {i.price or 'N/A'} | Tier: `{i.tier}`" for i in record.iap_items] or ["- Mağazada ayrıntılı IAP listesi yayınlanmamış."]
    rev_lines: list[str] = []
    for idx, r in enumerate(record.reviews[:25], start=1):
        snippet = sanitize_untrusted_text(r.text, max_len=360).replace("\n", " ")
        rev_lines.append(f"- **[EV-REV-{idx:02d}] {r.rating}★ ({r.date or '-'})**: {snippet}")
    if not rev_lines:
        rev_lines.append("- Yorum çekilemedi.")

    meta_md = f"""# Store Metadata Archive: {record.title}

> **Untrusted Data Notice:** Mağaza açıklamaları ve kullanıcı yorumları dış kaynaklı ham veridir; yalnızca analiz kanıtı olarak kullanılır.

- **Store:** `{record.store}`
- **App ID:** `{record.app_id}`
- **Store URL:** {record.store_url}
- **Developer:** {record.developer}
- **Category:** {record.category} ({", ".join(record.secondary_categories) or "-"})
- **Product Mode:** `{record.product_mode}`
- **Rating:** {record.rating}★ ({record.ratings_count:,} ratings) | **Installs:** {record.installs or "N/A"}
- **Price:** {"Free" if record.free else f"{record.price} {record.currency}"} | **Offers IAP:** {record.offers_iap} ({record.iap_price_range or "-"}) | **Contains Ads:** {record.ad_supported}
- **Version / Updated:** {record.version or "-"} ({record.last_updated or "-"})

## Subtitle / Short Description
{sanitize_untrusted_text(record.subtitle_or_short_desc, 400) or "-"}

## In-App Purchases (IAP Ladder)
{chr(10).join(iap_lines)}

## Full Description
```text
{sanitize_untrusted_text(record.description, 4500)}
```

## Recent User Reviews (Evidence Sample)
{chr(10).join(rev_lines)}
"""
    safe_join(app_dir, "store_metadata.md").write_text(meta_md, encoding="utf-8")

    web_blocks: list[str] = []
    for item in record.web_evidence:
        web_blocks.append(
            f"### [{item.evidence_id}] {item.title}\n"
            f"- **Category:** `{item.category}` | **Domain:** `{item.domain}`\n"
            f"- **URL:** {item.url}\n"
            f"- **Query:** `{item.query}`\n"
            f"- **Snippet:** {item.snippet or '-'}\n"
        )
    if not web_blocks:
        web_blocks.append(
            "_Otomatik web araması boş döndü veya ağ tarafından sınırlandı. Ajan, `search_web` aracını kullanarak gelir, reklam kadansı ve kullanıcı yorumları için ek kaynakları aşağıdaki alana ekleyebilir._"
        )

    web_md = f"""# Web Research & External Evidence: {record.title}

Bu dosya `{record.title}` için toplanan harici internet kanıtlarını (gelir tahminleri, monetizasyon analizleri, oyun/UX teardown yazıları) saklar.

## Collected Web Evidence ({len(record.web_evidence)} sources)

{chr(10).join(web_blocks)}

<!-- AGENT_WEB_ENRICHMENT_START -->
## Agent Deep Web Verification Notes
_Ajan, canlı `search_web` aramalarıyla elde ettiği ek gelir, reklam ağı, kullanıcı edinimi (UA) veya teardown verilerini kaynak URL'leriyle buraya ekler._
<!-- AGENT_WEB_ENRICHMENT_END -->
"""
    safe_join(app_dir, "web_research.md").write_text(web_md, encoding="utf-8")

    palette_rows = [
        f"| `{s.hex}` | `rgb{s.rgb}` | {s.ratio_pct:.1f}% | {s.luminance:.2f} | {s.temperature} |"
        for s in record.combined_palette
    ] or ["| - | - | - | - | - |"]

    vid_sections: list[str] = []
    frame_rows: list[str] = []
    for v_idx, v in enumerate(record.youtube_videos, start=1):
        sb_links = ", ".join(f"`{p}`" for p in v.storyboard_paths) or "-"
        vid_sections.append(
            f"- **[EV-VID-{v_idx:02d}] {v.title or 'Video'}** ({v.channel or '-'}, {v.view_count:,} izlenme, klip: {v.clip_duration_sec:.1f}s / toplam: {v.duration_sec:.0f}s)\n"
            f"  - YouTube: {v.url}\n"
            f"  - Lokal Video: `{v.local_path or '-'}` ({format_bytes(v.file_size_bytes)})\n"
            f"  - Storyboard'lar: {sb_links}\n"
            f"  - Çıkarılan Kare Sayısı: **{len(v.frames)}**"
        )
        for kf in v.frames:
            frame_rows.append(
                f"| `EV-FRAME-{v_idx:02d}-{kf.index:02d}` | `{kf.timestamp_label}` | `{kf.phase_hint}` | `{kf.source}` | `{', '.join(kf.dominant_colors[:3])}` | `{kf.local_path}` |"
            )

    if not vid_sections:
        vid_sections.append("- YouTube gameplay/walkthrough videosu indirilemedi.")
    if not frame_rows:
        frame_rows.append("| - | - | - | - | - | - |")

    friction_md = ", ".join(f"`{k}` ({v})" for k, v in sig.ux_friction_themes.items()) or "Belirgin tekrarlayan şikayet tespit edilmedi"
    praise_md = ", ".join(f"`{k}` ({v})" for k, v in sig.praise_themes.items()) or "Belirgin övgü kalıbı tespit edilmedi"
    ret_md = ", ".join(f"`{h}`" for h in sig.retention_hooks) or "Otomatik sinyal yok (karelerden kontrol et)"
    ads_md = ", ".join(f"`{a}`" for a in sig.detected_ad_formats) or "Otomatik reklam formatı tespit edilmedi"

    mode_label = "Mobil Oyun Teardown (Game Mode)" if record.product_mode == "game" else "Mobil Uygulama Teardown (App Mode)"

    teardown_md = f"""# Ürün & Rakip Teardown Raporu: {record.title}

- **Analiz Modu:** {mode_label}
- **Mağaza:** `{record.store}` | **ID:** `{record.app_id}` | **Geliştirici:** {record.developer}
- **Puan & Popülerlik:** {record.rating}★ ({record.ratings_count:,} oy) | İndirme: {record.installs or "N/A"} | Popülerlik Skoru: `{sig.popularity_score}`
- **Kanıt Tamlık Skoru:** **{sig.evidence_score}/100** (`evidence.json`)
- **Otomatik Tespit Edilen Gelir Modeli:** `{sig.monetization_model}`
- **IAP Fiyat Aralığı:** {record.iap_price_range or "-"} | **Abonelik:** `{sig.has_subscription}` | **Reklamsız Paket:** `{sig.has_remove_ads}` | **Battle/Season Pass:** `{sig.has_battle_pass}`

## 1. İndirilen Kanıt & Medya Envanteri
- **Mağaza Arşivi:** `store_metadata.md` (`EV-STORE-01`)
- **Mağaza Ekran Görüntüsü Sheet:** `{record.screenshots_sheet_path or "-"}` (`EV-SHOTS-01`)
- **Renk Paleti Kartı:** `{record.palette_card_path or "-"}` (`EV-PALETTE-01`)
- **Web Araştırma Kanıtları:** `web_research.md` ({len(record.web_evidence)} kaynak)
{chr(10).join(vid_sections)}

## 2. Otomatik Sinyal Özeti (Mağaza + Yorum + Medya)
- **Tespit Edilen Reklam Formatları:** {ads_md}
- **Reklam Şikayeti Oranı (Yorumlar):** %{sig.ad_complaint_ratio_pct} | **Paywall/Fiyat Şikayeti Oranı:** %{sig.paywall_complaint_ratio_pct}
- **Tespit Edilen Retention Mekanikleri:** {ret_md}
- **Yorumlardaki Sürtünme (Friction) Temaları:** {friction_md}
- **Yorumlardaki Güçlü Yönler (Praise):** {praise_md}

## 3. Çıkarılan Renk Paleti (HEX Kanıt Tablosu)
| HEX | RGB | Baskınlık | Parlaklık (0-1) | Sıcaklık |
| :--- | :--- | ---: | ---: | :--- |
{chr(10).join(palette_rows)}

## 4. Kare Kare Video Zaman Çizelgesi (Kanıt İndeksi)
| Evidence ID | Zaman | Faz Tahmini | Kaynak | Baskın Renkler | Dosya Yolu |
| :--- | :--- | :--- | :--- | :--- | :--- |
{chr(10).join(frame_rows)}

<!-- AGENT_TEARDOWN_ANALYSIS_START -->
## 5. Derin Multimodal Ürün & Kare Kare Analiz (Ajan İncelemesi Bekliyor)

> **Ajan Talimatı:** Yukarıdaki storyboard'ları, kritik kareleri (`gameplay_frames/`), `store_screenshots_sheet.png`, `color_palette_card.png` ve `web_research.md` dosyalarını bizzat inceleyerek aşağıdaki 7 başlığı kanıt ID'leriyle (`[EV-FRAME-01-03]`, `[EV-WEB-01]`, `[EV-REV-02]`) doldur.

### 5.1 UI/UX Dizilimi & Bilgi Mimarisi
- *(Ekran yönü, HUD / tab bar yerleşimi, başparmak erişim bölgesi, safe-area kullanımı, menü hiyerarşisi ve görsel yoğunluk.)*

### 5.2 Oynanış Mekaniği / Core Loop & Game Feel (veya Temel Kullanıcı Akışı)
- *(İlk 10 saniye aksiyonu, temel döngü, kontrol şeması, mikro geri bildirim / juice, zorluk veya değer eğrisi.)*

### 5.3 Renk Paleti, Tipografi & Sanat Yönü
- *(Arka plan vs odak nesnesi kontrastı, etkileşimli CTA renkleri, renk sıcaklığı ve görsel okunabilirlik.)*

### 5.4 Göze Çarpan Kısımlar (Visual Hooks & Wow Moments)
- *(Kullanıcıyı ilk 30 saniyede yakalayan özgün tasarım/mekanik kararları ve dönüşüm tetikleyicileri.)*

### 5.5 Satın Alım (IAP / Paywall) & Reklam Dizilimi
- *(İlk reklam/paywall ne zaman çıkıyor? Interstitial, rewarded, banner veya abonelik ekranlarının akıştaki yeri ve fiyat çıpalama taktikleri.)*

### 5.6 Kullanıcıyı Elde Tutma Stratejisi (Retention & Habit Loops)
- *(FTUE/onboarding, D1/D7/D30 geri dönüş kancaları, günlük ödül/görev/meta-progression veya alışkanlık döngüleri.)*

### 5.7 Gelir Stratejisi & Net Çıkarımlar
- *(Gelir motorunun özeti, kopyalanacak 3 en iyi pratik ve bu rakibin açık bıraktığı 3 tasarım fırsatı.)*
<!-- AGENT_TEARDOWN_ANALYSIS_END -->
"""
    safe_join(app_dir, "teardown_report.md").write_text(teardown_md, encoding="utf-8")


def write_domain_and_kits_reports(run: TeardownRun, run_dir: Path) -> None:
    """Write DOMAIN_ARASTIRMASI.md, FREE_ASSET_VE_KIT_REHBERI.md, and JSON evidence files."""
    ev_dir = safe_join(run_dir, "evidence")
    ev_dir.mkdir(parents=True, exist_ok=True)

    # 1. Domain / Subject-Matter Research
    safe_join(ev_dir, "domain_sources.json").write_text(
        json.dumps([d.__dict__ for d in run.domain_evidence], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    brief = run.idea_brief
    idea_text = brief.raw_idea if brief and brief.raw_idea else (run.query or run.campaign_name)
    theme_text = brief.theme_label if brief and brief.theme_label else run.query
    topics_list = brief.domain_topics if brief else []

    dom_blocks: list[str] = []
    for item in run.domain_evidence:
        dom_blocks.append(
            f"### [{item.evidence_id}] {item.title}\n"
            f"- **Konu / Sorgu:** `{item.topic}`\n"
            f"- **Kaynak:** `{item.domain}` | **URL:** {item.url}\n"
            f"- **Özet:** {item.snippet or '-'}\n"
        )
    if not dom_blocks:
        dom_blocks.append(
            "_Otomatik domain araması boş döndü veya konu belirtilmedi. Ajan, canlı `search_web` aracıyla ürün temasının gerçek dünya kurallarını (ör. hamburger katman dizilimi, pişirme aşamaları, tarif/içerik kombinasyonları) araştırıp aşağıya işler._"
        )

    domain_md = f"""# Alan & Konu (Domain) Araştırması: {theme_text}

Bu doküman, rakip uygulama analizinden ayrı olarak tasarlanacak ürünün **gerçek dünya konu bilgisini** inceler. (Örneğin: kapılı yemek yapma oyununda hamburger katman sırası, pişirme evreleri, müşteri sipariş çeşitleri; alışkanlık uygulamasında davranış psikolojisi kuralları.)

- **Kullanıcı Fikri:** {idea_text}
- **Rakip Mekanik Sorgusu (Kategori Ekseni):** `{brief.mechanic_query if brief else run.query}`
- **Araştırılan Domain Başlıkları (Tema Ekseni):** {", ".join(f"`{t}`" for t in topics_list) or "-"}

## Toplanan Web Kanıtları ({len(run.domain_evidence)} kaynak)

{chr(10).join(dom_blocks)}

<!-- AGENT_DOMAIN_SYNTHESIS_START -->
## Ajan Domain Sentezi & Oyun/Uygulama İçerik Kuralları

> **Ajan Talimatı:** Yukarıdaki kanıtları ve gerekirse ek canlı `search_web` sonuçlarını birleştirerek oyunun veya uygulamanın konu mantığını somutlaştır:
> - **Gerçek Dünya Anatomisi / Sıralama Kuralları:** *(Örn. Hamburger katman sırası: Alt ekmek -> Sos -> Marul -> Köfte -> Peynir -> Domates -> Turşu -> Üst ekmek; yanlış/eksik katman veya yanık köfte puan kuralı.)*
> - **İçerik / Seviye Çeşitlendirme Tablosu:** *(Başlangıç -> Orta -> İleri seviye yeni malzeme, tarif veya özellik açılış sırası.)*
> - **Görsel & İşitsel Gerçekçilik İpuçları:** *(Kullanıcının anında tanımasını sağlayan silüet, renk ve ses ipuçları.)*
<!-- AGENT_DOMAIN_SYNTHESIS_END -->
"""
    safe_join(run_dir, "DOMAIN_ARASTIRMASI.md").write_text(domain_md, encoding="utf-8")

    # 2. Free UI/UX, 3D/2D Model, Audio/SFX, Font & Engine SDK Kits
    safe_join(ev_dir, "free_kits.json").write_text(
        json.dumps([k.__dict__ for k in run.free_asset_kits], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    cat_titles = [
        ("ui_ux", "1. Ücretsiz UI / UX Kitleri & İkon Paketleri"),
        ("models_sprites", "2. Ücretsiz 3D / 2D Model & Sprite Paketleri"),
        ("audio_sfx", "3. Ücretsiz Ses Efekti (SFX) & Müzik Kitleri"),
        ("fonts", "4. Ücretsiz Font Eşleşmeleri"),
        ("engine_sdk", "5. Seçilen Teknoloji İçin Ücretsiz Eklenti, Shader & Monetizasyon SDK'ları"),
    ]

    kit_sections: list[str] = []
    for cat_key, heading in cat_titles:
        subset = [k for k in run.free_asset_kits if k.category == cat_key]
        kit_sections.append(f"## {heading}\n")
        if not subset:
            kit_sections.append("_Bu kategoride henüz kayıt yok._\n")
            continue
        kit_sections.append("| ID | Kit / Kaynak Adı | Lisans | Format | Kullanım & Uyumluluk | Bağlantı |")
        kit_sections.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for k in subset:
            fmts = ", ".join(k.formats) or "-"
            note = k.usage_note.replace("|", "/").replace("\n", " ")
            kit_sections.append(
                f"| `{k.evidence_id}` | **{k.name}** ({k.source}) | `{k.license}` | {fmts} | {note} | [Aç]({k.url}) |"
            )
        kit_sections.append("")

    chosen_tech = brief.selected_tech if brief and brief.selected_tech else "(Henüz sabitlenmedi)"
    kits_md = f"""# Ücretsiz Üretim Asset, UI/UX, Model & Ses Kitleri Rehberi

- **Proje Fikri:** {idea_text}
- **Tema / Sanat Ekseni:** `{theme_text}`
- **Seçilen Teknoloji:** `{chosen_tech}`
- **Toplam Doğrulanmış / Bulunan Kit:** **{len(run.free_asset_kits)}** (`evidence/free_kits.json`)

> **Lisans Notu:** `CC0 1.0`, `MIT` ve `SIL OFL` paketler ticari mobil oyun/uygulamalarda atıf gerektirmeden kullanılabilir. `CC BY` veya canlı web aramasından (`web_search`) gelen kaynakların indirme sayfasındaki güncel lisans şartını yayın öncesi son kez doğrula.

{chr(10).join(kit_sections)}

<!-- AGENT_EXTRA_KITS_START -->
## Ajan Tarafından Eklenen Temaya Özel Ücretsiz Kaynaklar & Asset Eşleştirme Haritası
> **Ajan Talimatı:** Canlı `search_web` ile bulduğun ek ücretsiz UI/UX, 3D/2D model veya ses efekt kitlerini buraya ekle ve her oyun/uygulama olayının (ör. kapıdan geçme sesi, katman ekleme pop sesi, kazanma fanfarı, buton paketi, ana karakter/malzeme modeli) hangi kit dosyasından karşılanacağını eşleştir.
<!-- AGENT_EXTRA_KITS_END -->
"""
    safe_join(run_dir, "FREE_ASSET_VE_KIT_REHBERI.md").write_text(kits_md, encoding="utf-8")


def write_campaign_reports(run: TeardownRun, run_dir: Path) -> None:
    """Write GENEL_TEARDOWN_RAPORU.md, DOMAIN_ARASTIRMASI.md, FREE_ASSET_VE_KIT_REHBERI.md, TASARIM_BLUEPRINT.md, and indices."""
    ca = run.cross_analysis
    comps = run.competitors
    brief = run.idea_brief

    # 1. run_config.json & apps_index.json
    safe_join(run_dir, "run_config.json").write_text(
        json.dumps({
            "run_id": run.run_id,
            "campaign_name": run.campaign_name,
            "query": run.query,
            "product_mode": run.product_mode,
            "stores": run.stores,
            "country": run.country,
            "lang": run.lang,
            "limit_per_store": run.limit_per_store,
            "max_video_sec": run.max_video_sec,
            "max_frames": run.max_frames,
            "created_at": run.created_at,
            "competitor_count": len(comps),
            "idea": brief.raw_idea if brief else "",
            "selected_tech": brief.selected_tech if brief else "",
            "theme_label": brief.theme_label if brief else "",
            "domain_topics": brief.domain_topics if brief else [],
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    safe_join(run_dir, "apps_index.json").write_text(
        json.dumps(run.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 2. apps_index.csv
    csv_path = safe_join(run_dir, "apps_index.csv")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "store", "app_id", "title", "developer", "category", "mode",
            "rating", "ratings_count", "installs", "monetization_model",
            "iap_range", "ad_formats", "retention_hooks", "video_frames",
            "web_sources", "evidence_score", "folder_name",
        ])
        for c in comps:
            writer.writerow([
                c.store, c.app_id, c.title, c.developer, c.category, c.product_mode,
                c.rating, c.ratings_count, c.installs, c.signals.monetization_model,
                c.iap_price_range, "; ".join(c.signals.detected_ad_formats),
                "; ".join(c.signals.retention_hooks),
                sum(len(v.frames) for v in c.youtube_videos),
                len(c.web_evidence), c.signals.evidence_score, c.folder_name,
            ])

    # 3. Domain Research & Free Asset Kits reports
    write_domain_and_kits_reports(run, run_dir)

    # 4. GENEL_TEARDOWN_RAPORU.md
    matrix_rows: list[str] = []
    for c in comps:
        frames_cnt = sum(len(v.frames) for v in c.youtube_videos)
        hex_preview = " ".join(f"`{s.hex}`" for s in c.combined_palette[:3]) or "-"
        matrix_rows.append(
            f"| [{c.title}](apps/{c.folder_name}/teardown_report.md) | `{c.store}` | `{c.product_mode}` | {c.rating}★ ({c.ratings_count:,}) | {c.signals.monetization_model} | {frames_cnt} kare | {len(c.web_evidence)} kaynak | {hex_preview} | **{c.signals.evidence_score}/100** |"
        )
    if not matrix_rows:
        matrix_rows.append("| - | - | - | - | - | - | - | - | - |")

    def _dict_bullets(d: dict[str, Any], empty_msg: str) -> str:
        if not d:
            return f"- {empty_msg}"
        return "\n".join(f"- **{k}:** {v}" for k, v in d.items())

    genel_md = f"""# Genel Rakip Teardown & Ürün Zekası Raporu: {run.campaign_name}

- **Proje Fikri:** {brief.raw_idea if brief and brief.raw_idea else "-"}
- **Seçilen Teknoloji:** `{brief.selected_tech if brief and brief.selected_tech else "Belirtilmedi"}`
- **Rakip Mekanik Sorgusu:** `{run.query or "Direct Targets"}`
- **Bölge / Dil:** `{run.country.upper()} / {run.lang}` | **Baskın Mod:** `{ca.get("dominant_mode", run.product_mode)}`
- **Analiz Edilen Rakip:** **{len(comps)}** | **Toplam Video Karesi:** **{ca.get("total_gameplay_frames", 0)}** | **Web Kanıtı:** **{ca.get("total_web_evidence_sources", 0)}** | **Domain Kanıtı:** **{len(run.domain_evidence)}** | **Ücretsiz Kit:** **{len(run.free_asset_kits)}**
- **İlgili Raporlar:** `DOMAIN_ARASTIRMASI.md` | `FREE_ASSET_VE_KIT_REHBERI.md` | `TASARIM_BLUEPRINT.md` | `dashboard.html`

## 1. Rakip Karşılaştırma Matrisi
| Uygulama / Oyun | Mağaza | Mod | Puan & Hacim | Gelir Modeli | Kare Kanıtı | Web Kanıtı | Baskın Palet | Kanıt Skoru |
| :--- | :--- | :--- | :--- | :--- | ---: | ---: | :--- | ---: |
{chr(10).join(matrix_rows)}

## 2. Kategori Monetizasyon & Reklam Dağılımı
### Gelir Modelleri
{_dict_bullets(ca.get("monetization_breakdown", {}), "Veri yok")}

### Tespit Edilen Reklam Formatları
{_dict_bullets(ca.get("ad_format_adoption", {}), "Veri yok")}

## 3. Kullanıcıyı Elde Tutma (Retention) Sütunları
{_dict_bullets(ca.get("retention_pillars", {}), "Veri yok")}

## 4. Yorumlardan Çıkan Ortak Sürtünmeler (Açık Fırsatlar) & Övgü Faktörleri
### En Çok Şikayet Edilen Alanlar (Farklılaşma Fırsatı)
{_dict_bullets(ca.get("shared_ux_frictions", {}), "Veri yok")}

### Kullanıcıları Bağlayan Güçlü Yönler
{_dict_bullets(ca.get("top_praise_drivers", {}), "Veri yok")}

## 5. Görsel Sıcaklık & Renk Kümelemesi
- **Renk Sıcaklığı Dağılımı:** {ca.get("color_temperature_mix", {})}
- **Kategoride Sık Görülen HEX Tonları:** {", ".join(f"`{h}`" for h in ca.get("sample_dominant_hexes", [])) or "-"}

<!-- AGENT_MASTER_SYNTHESIS_START -->
## 6. Çapraz Ürün Sentezi (Ajan Multimodal İnceleme Sonrası)

> **Ajan Talimatı:** Her rakibin `teardown_report.md` dosyasını kare kare tamamladıktan sonra kategorideki kazanan UI/UX düzenini, oynanış/akış kalıplarını, ideal reklam/paywall zamanlamasını, retention döngülerini ve pazarda boş bırakılan tasarım fırsatlarını kanıt referanslarıyla sentezle.
<!-- AGENT_MASTER_SYNTHESIS_END -->
"""
    safe_join(run_dir, "GENEL_TEARDOWN_RAPORU.md").write_text(genel_md, encoding="utf-8")

    # 5. TASARIM_BLUEPRINT.md (End-to-end buildable Game/App Design & Tech Blueprint)
    tech_prof = get_tech_profile(brief.selected_tech) if brief and brief.selected_tech else None
    tech_block = ""
    if tech_prof:
        arch_bullets = "\n".join(f"- {line}" for line in tech_prof.architecture_notes)
        tech_block = f"""### Seçilen Teknoloji Yığını: {tech_prof.name}
- **Lisans / Maliyet:** {tech_prof.license_cost} | **Karmaşıklık:** {tech_prof.complexity}
- **Desteklenen Asset Formatları:** {", ".join(tech_prof.asset_formats)}
- **Önerilen Teknik Mimari İskeleti:**
{arch_bullets}
"""
    else:
        tech_block = "- *(Seçilen teknoloji belirtilmedi; `plan-idea` çıktısındaki seçeneklere göre kullanıcıyla netleştir ve mimari iskeleti buraya yaz.)*\n"

    kit_preview_lines = [
        f"- **[{k.evidence_id}] ({k.category}) {k.name}** (`{k.license}`): {k.usage_note} -> {k.url}"
        for k in run.free_asset_kits[:16]
    ] or ["- `FREE_ASSET_VE_KIT_REHBERI.md` dosyasındaki kitleri buraya eşleştir."]

    blueprint_md = f"""# Uçtan Uca Uygulama / Oyun Tasarım Blueprint'i: {run.campaign_name}

Bu doküman; incelenen **{len(comps)} popüler rakibin** mağaza verileri, YouTube kare analizleri, **domain konu araştırması** (`DOMAIN_ARASTIRMASI.md`) ve **ücretsiz üretim kitleri** (`FREE_ASSET_VE_KIT_REHBERI.md`) birleştirilerek sıfırdan üretime alınabilecek eksiksiz tasarım planını sunar.

## 0. Fikir, Araştırma Ayrımı & Teknoloji Kararı
- **Ham Ürün Fikri:** {brief.raw_idea if brief and brief.raw_idea else (run.query or run.campaign_name)}
- **Rakip Benchmark Ekseni (Mekanik):** `{brief.mechanic_query if brief else run.query}`
- **Domain & Tema Ekseni (Konu Bilgisi):** `{brief.theme_label if brief else "-"}`

{tech_block}

<!-- AGENT_BLUEPRINT_START -->
## 1. Konumlandırma & Farklılaşma Tezi
- **Hedef Kategori & Mod:** `{ca.get("dominant_mode", run.product_mode)}`
- **Rakiplerin Ortak Zayıf Noktaları (Bizim Avantajımız):** {", ".join(ca.get("shared_ux_frictions", {}).keys()) or "(Ajan incelemesi sonrası doldurulacak)"}
- **Tek Cümlelik Ürün Vaadi:** *(Ajan, kullanıcının fikrine ve rakip boşluklarına göre doldurur.)*

## 2. Domain Kuralları & İçerik Tasarımı (`DOMAIN_ARASTIRMASI.md` Kaynaklı)
- **Gerçek Dünya Mantığı & Katman/Akış Kuralları:** *(Örn. hamburger katman dizilimi, doğru/yanlış kapı etkileri, sipariş eşleştirme puanı veya uygulama konu kuralları.)*
- **İçerik İlerleme Tablosu (Seviye 1 -> Seviye 20+):**

## 3. Çekirdek Döngü (Core Loop), Mekanikler & MVP Kapsamı
- **İlk 30 Saniye (FTUE / Aha Anı):**
- **Temel Oynanış / Kullanım Döngüsü:**
- **Göze Çarpan "Wow" Mekanikleri & Game Feel / UX Detayları:**
- **MVP'ye Dahil Edilecekler vs v1.1'e Bırakılacaklar:**

## 4. Ekran Ekran UI/UX & Navigasyon Mimarisi
- **Ekran Yönü & Safe-Area Politikası:**
- **Ana Ekran / HUD Yerleşimi (Üst Bar, Odak Alanı, Alt Bar / Başparmak Bölgesi):**
- **Ekran Akışı (Splash -> Onboarding -> Core Screen -> Reward/Result -> Shop/Paywall -> Meta):**

## 5. Renk Paleti & Görsel Tasarım Sistemi
- **Kategorideki Mevcut Renk Yoğunlaşması:** {", ".join(f"`{h}`" for h in ca.get("sample_dominant_hexes", [])[:6]) or "-"}
- **Önerilen Ayrışma Paleti (Primary / Secondary / Accent / Surface / Danger / Reward HEX Tokenları):**

## 6. Ücretsiz UI/UX, 3D/2D Model, Ses & Eklenti Reçetesi (`FREE_ASSET_VE_KIT_REHBERI.md`)
{chr(10).join(kit_preview_lines)}

## 7. Gelir, Satın Alım (IAP/Paywall) & Reklam Dizilimi
- **Önerilen Gelir Modeli:** `{ca.get("dominant_monetization", "Hybrid")}`
- **Reklam Yerleşim Haritası (Interstitial zamanlama, Rewarded değer teklifi, Banner kuralı):**
- **IAP / Abonelik Fiyat Merdiveni (Entry / Anchor / Pro / Remove-Ads / Pass):**
- **Paywall Tetikleme Anları (Değer anı sonrası, agresiflik sınırı):**

## 8. Kullanıcıyı Elde Tutma Stratejisi (D1 / D7 / D30)
- **D1 (İlk Gün):**
- **D7 (İlk Hafta):**
- **D30 (Uzun Vadeli Meta & Live-Ops / Alışkanlık Döngüsü):**

## 9. Seçilen Teknolojiye Özel Uygulama Yol Haritası (Sprint Planı)
- **Sprint 1 (Gri Kutu Prototip & Core Loop):**
- **Sprint 2 (Domain İçeriği, Ücretsiz 3D/2D Modeller & HUD/UI Kit Entegrasyonu):**
- **Sprint 3 (Game Feel/Juice, Ücretsiz SFX/Ses Katmanı & Seviye Dengeleme):**
- **Sprint 4 (Reklam/IAP SDK Entegrasyonu, Telemetri & Mağaza Yayın Hazırlığı):**
<!-- AGENT_BLUEPRINT_END -->
"""
    safe_join(run_dir, "TASARIM_BLUEPRINT.md").write_text(blueprint_md, encoding="utf-8")
