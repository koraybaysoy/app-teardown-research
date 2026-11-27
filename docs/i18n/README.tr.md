<div align="center">

# App & Game Teardown Research Toolkit

**Yeni bir mobil uygulama veya oyun tasarlamadan önce rakip ürün analizi: App Store & Google Play en popüler 5 rakip keşfi, YouTube oynanış/walkthrough kare kare ayrıştırma, HEX renk paleti kartları, web kanıt arşivi ve üretime hazır tasarım blueprint aracı.**

<p>
  <a href="../../README.md">English</a> ·
  <strong>Türkçe</strong> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## Ne İşe Yarar?

Yeni bir hypercasual oyun, hibrit oyun veya tüketici/SaaS mobil uygulaması tasarlamadan önce pazardaki en popüler rakipleri tek tek indirip ekran kaydı almak, YouTube videolarını durdurup HUD ve paywall dizilimini incelemek, renk kodlarını çıkarmak ve gelir/retention makalelerini toplamak günler sürer.

Bu plugin tüm süreci **sıfır API maliyetiyle lokal makinenizde** otomatikleştirir:

- **Adım 0 — Fikir Analizi, Teknoloji Danışmanı & Mekanik/Domain Ayrımı (`plan-idea`):** Kullanıcı fikrini yazar (ör. *"kapılardan geçtiğin hypercasual yemek/hamburger oyunu"*). Tool önce 3 teknoloji seçeneği (**Godot 4**, **Unity 6**, **Phaser/Web** veya uygulama için **Flutter**, **React Native**, **Native**) önerip kullanıcıya sorar; ardından **Mekanik Rakip Araştırması** (*hypercasual runner/gate* liderleri) ile **Gerçek Dünya Domain Araştırması** (*hamburger katman dizilimi, pişirme evreleri, sipariş kombinasyonları*) eksenlerini birbirinden ayırır.
- **Ücretsiz UI/UX, 3D/2D Model, Ses/SFX & SDK Kit Bulucu (`find-kits`):** Seçilen teknolojiye (ör. Godot 4) ve temaya uygun doğrulanmış ücretsiz (`CC0`, `MIT`, `SIL OFL`) UI/UX kitlerini (Kenney UI, Figma Community, Game-Icons), 3D/2D model paketlerini (Kenney Food Kit, KayKit, Quaternius, Poly Pizza), ses/SFX kitlerini (Kenney Audio, Freesound CC0, Mixkit) ve eklentileri **`FREE_ASSET_VE_KIT_REHBERI.md`** dosyasında toplar.
- **Çift Mağaza Popüler Rakip Keşfi (App Store + Google Play):** Hedef mekanikte en popüler 5 uygulamayı (indirme, oy hacmi ve puan ağırlıklı) bulur; IAP fiyat merdivenini, reklam bayraklarını, ekran görüntülerini ve kullanıcı yorumlarını arşivler.
- **YouTube Oynanış & Uygulama Turu Hasadı (`yt-dlp`):** Her rakip için temiz no-commentary mobil gameplay (Oyun Modu) veya uygulama UI/onboarding walkthrough (Uygulama Modu) videosunu otomatik arayıp ilk 4 dakikasını güvenli limitlerle indirir.
- **Hibrit Kare Kare Çıkarma & Renk Paleti Motoru (`FFmpeg` + `Pillow`):** Sahne değişimi algılama (`scene_change`) + zaman aralıklı örnekleme ile uygulama başı 24 kare çıkarır, zaman damgalı 3x4 storyboard'lar ve ölçülü **`color_palette_card.png`** HEX kartelaları üretir.
- **Çift Modlu Ürün Teardown Çerçevesi (Oyun + Genel Uygulama):**
  - UI/UX dizilimi, HUD/navigasyon ve başparmak bölgesi
  - Oynanış mekaniği, core loop, kontrol & game feel (veya uygulama aktivasyon/aha akışı)
  - Renk paletleri, görsel kontrast ve sanat yönü
  - Göze çarpan kısımlar (visual hooks, juice, UX delights)
  - Satın alım (IAP/paywall/abonelik) ve reklam dizilimi (interstitial, rewarded, banner)
  - Kullanıcıyı elde tutma (FTUE, D1/D7/D30 retention, meta-progression, alışkanlık döngüleri)
  - Gelir stratejisi & büyüme modeli
- **API-Keysiz Web Kanıt Arşivi + Kanıt İndeksi (`evidence.json`):** Her rakip için gelir, monetizasyon ve UX teardown kaynaklarını `web_research.md` ve `evidence/web_sources.json` dosyalarına kaydeder; her bulguyu benzersiz kanıt ID'leriyle (`EV-FRAME-01-04`, `EV-WEB-02`, `EV-REV-03`) izlenebilir tutar.
- **Raporlar, Tasarım Blueprint'i & Lokal Görsel Stüdyo (`dashboard.html`):** Uygulama bazlı `teardown_report.md`, çapraz sentez `GENEL_TEARDOWN_RAPORU.md`, kendi uygulamanız için `TASARIM_BLUEPRINT.md` ve CSP korumalı etkileşimli `dashboard.html` üretir.

## Hızlı Kurulum

### Windows (PowerShell)
```powershell
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
.\setup.ps1
```

### macOS / Linux
```bash
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh
```

*(Sistem `PATH` içinde Python 3.11+ ve `ffmpeg` bulunmalıdır.)*

## Plugin / Skill Kurulumu

```bash
# Evrensel Agent Skills (Antigravity, Claude Code, Codex, Cursor, Copilot)
npx skills add https://github.com/koraybaysoy/app-teardown-research
```

- **Antigravity:** Kök dizindeki `plugin.json`, `mcp_config.json`, `.agents/skills/` ve `.agents/rules/` ile doğrudan hazır.
- **Claude Code:** `/plugin install app-teardown --marketplace koraybaysoy/app-teardown-research`
- **Cursor:** `.cursor-plugin/`, `.cursor/rules/app-teardown.mdc` ve `.mcp.json` dahildir.

## Temel CLI Kullanımı

```powershell
# 1. En popüler 5 rakibi önizle
.\.venv\Scripts\python.exe -m app_teardown.cli discover "hypercasual runner" --stores both --country us --lang en --limit 5

# 2. Tam ürün teardown'ı çalıştır (YouTube kareleri + HEX palet + web kanıt + raporlar + dashboard)
.\.venv\Scripts\python.exe -m app_teardown.cli teardown --query "hypercasual runner" --stores both --mode game --limit 5 --name "hypercasual-runner"

# 3. Tek bir YouTube videosundan kare + renk paleti çıkar
.\.venv\Scripts\python.exe -m app_teardown.cli extract-video "https://www.youtube.com/watch?v=..." --out "teardowns/tek-video"

# 4. Mevcut kampanyanın rapor ve dashboard'unu yeniden üret
.\.venv\Scripts\python.exe -m app_teardown.cli rebuild "teardowns/<kampanya_klasoru>"
```

## Lisans

[MIT](../../LICENSE)
