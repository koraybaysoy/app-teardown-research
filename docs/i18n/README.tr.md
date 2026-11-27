<div align="center">

# App & Game Teardown Research Toolkit

**Yeni bir mobil uygulama veya mobil oyun kodlamadan önce tam rakip analizi ve ürün teardown aracı. Teknoloji yığınını seç, App Store ve Google Play'deki en popüler 5 rakibi YouTube oynanış kareleriyle incele, konu (domain) araştırmasını yap, ücretsiz CC0 UI/UX, 3D model ve ses kitlerini topla ve üretime hazır tasarım blueprint'i çıkar.**

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

## Neden Var?

Yeni bir hypercasual oyun ya da tüketici uygulaması tasarlarken rakip araştırması çoğu zaman günler alır. Rakipleri tek tek indirirsin. YouTube videolarını durdurup HUD dizilimine, paywall zamanlamasına ve reklam sıklığına bakarsın. Renk paleti kodlarını çıkarıp gelir ve retention yazılarını ayrı ayrı toplarsın.

Bu Python eklentisi tüm ürün teardown sürecini API ücreti olmadan kendi bilgisayarında çalıştırır. Aklındaki fikri yazarsın. Araç önce uygun teknolojileri (Godot, Unity, Phaser, Flutter, React Native veya Native) karşılaştırıp kararı sana sorar. Seçimini yaptığında Google Play ve App Store'daki en popüler 5 rakibi tarar, YouTube oynanış ya da uygulama turu videolarından FFmpeg ile kare çıkarma yapar, HEX renk paleti kartları üretir, web kanıtlarını arşivler, ücretsiz asset kitlerini bulur ve AI ajanlarının (Antigravity, Claude Code, Codex, Cursor, GitHub Copilot) doğrudan kullanabileceği kanıtlı bir tasarım blueprint'i hazırlar.

## Ne Yapar?

- **Adım 0: Fikir Analizi, Teknoloji Seçimi ve Mekanik / Domain Ayrımı (`plan-idea`):**
  - Ham fikrini okur ve 3 uygun teknoloji seçeneğini artıları, eksileri ve maliyetiyle sıralar (oyunlar için Godot 4, Unity 6, Phaser; uygulamalar için Flutter, React Native, Native). Kararı sen verirsin.
  - Rakip araştırması ile konu bilgisini ayırır. Örnek: kapılardan geçip hamburger yapılan bir hypercasual oyun istiyorsan mağazada yemek tarifi uygulamalarını değil, en popüler hypercasual runner ve kapı mekaniği oyunlarını tarar. Eş zamanlı olarak hamburger katman sırası, pişirme evreleri ve malzeme kurallarını araştırıp `DOMAIN_ARASTIRMASI.md` dosyasına yazar.
- **Ücretsiz UI/UX, 3D/2D Model, Ses/SFX, Font ve SDK Kit Bulucu (`find-kits`):**
  - Seçtiğin motora ve temaya uyan doğrulanmış ücretsiz (`CC0 1.0`, `MIT`, `SIL OFL`, telifsiz) paketleri derler ve web'de ek kaynak arar.
  - UI/UX kitleri (Kenney UI, Figma Community, Game-Icons, Lucide), 3D/2D modeller (Kenney Food Kit, KayKit, Quaternius, Poly Pizza), ses efektleri (Kenney Audio, Freesound CC0, Mixkit), Google Fonts ve motor eklentileri (Godot AdMob, PhantomCamera, Godot Shaders, RevenueCat) `FREE_ASSET_VE_KIT_REHBERI.md` içinde listelenir.
- **App Store ve Google Play Popüler İlk 5 Keşfi (API Anahtarsız):**
  - Google Play ve Apple App Store sonuçlarını indirme hacmi, oy sayısı, puan ve alaka dengesiyle sıralar.
  - Mağaza metinlerini, IAP fiyat merdivenini, reklam bayraklarını, ikonları, ekran görüntülerini ve 30'dan fazla kullanıcı yorumunu indirir. Reklam bıkkınlığı, paywall şikayetleri ve öne çıkan övgü başlıklarını otomatik çıkarır.
- **YouTube Oynanış ve Uygulama Turu İndirici (`yt-dlp`):**
  - Oyun modunda yorumsuz mobil oynanış videolarını, uygulama modunda UI ve onboarding turlarını YouTube üzerinden arayıp puanlar. İlk 4 dakikalık bölümü güvenli boyut sınırıyla indirerek açılış, ilk deneyim (FTUE), temel döngü ve erken gelir ekranlarını yakalar.
- **Hibrit Kare Çıkarma ve HEX Renk Paleti Motoru (`FFmpeg` + `Pillow`):**
  - `ffmpeg` sahne değişimi algılaması ile düzenli zaman aralığını birleştirerek uygulama başı 24 kare çıkarır. Menü, oynanış, reklam ve paywall geçişleri tek tek kaydedilir.
  - Zaman damgalı 3x4 storyboard'lar (`gameplay_01_storyboard_*.png`), tam boy kareler ve HEX kodlu `color_palette_card.png` kartelaları üretir.
- **Oyun Modu ve Genel Uygulama Modu Analizi:**
  - **Oyun Modu:** UI/UX ve HUD yerleşimi, çekirdek oynanış döngüsü, kontrol ve oyun hissi, renk paleti kontrastı, göze çarpan kancalar, reklam dizilimi (interstitial, rewarded, banner), IAP ekonomisi ve D1/D7/D30 retention stratejisi.
  - **Uygulama Modu:** Onboarding ve ilk değer anı, navigasyon ve başparmak bölgesi, görsel tasarım sistemi, paywall zamanlaması ve fiyat çıpalama, alışkanlık döngüleri ve iptal (churn) nedenleri.
- **Web Kanıt Arşivi ve Kanıt İndeksi (`evidence.json`):**
  - Gelir stratejisi, indirme tahminleri ve ürün teardown yazılarını `web_research.md` ile `evidence/web_sources.json` dosyalarında saklar.
  - Her bulguya benzersiz bir kanıt kodu verir (`EV-STORE-01`, `EV-VID-01`, `EV-FRAME-01-04`, `EV-PALETTE-01`, `EV-WEB-02`, `EV-DOM-01`, `EV-KIT-01`). Raporlardaki her yargı yerel bir kareye ya da URL'ye dayanır.
- **Raporlar, Tasarım Blueprint'i ve Yerel Stüdyo (`dashboard.html`):**
  - Rakip başı `teardown_report.md`, `web_research.md`, `store_metadata.md` ve `evidence.json` dosyalarını üretir. Kampanya kökünde `GENEL_TEARDOWN_RAPORU.md`, `DOMAIN_ARASTIRMASI.md`, `FREE_ASSET_VE_KIT_REHBERI.md`, `TASARIM_BLUEPRINT.md`, `apps_index.csv` ve CSP korumalı etkileşimli `dashboard.html` yer alır.

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

*(Sistem `PATH` içinde Python 3.11+ ve `ffmpeg` kurulu olmalı.)*

## Plugin ve Agent Skills Kurulumu

```bash
# Evrensel Agent Skills (Antigravity, Claude Code, Codex, Cursor, GitHub Copilot)
npx skills add https://github.com/koraybaysoy/app-teardown-research
```

- **Antigravity:** Kök dizindeki `plugin.json`, `mcp_config.json`, `.agents/skills/` ve `.agents/rules/` ile doğrudan çalışır.
- **Claude Code:** `/plugin install app-teardown --marketplace koraybaysoy/app-teardown-research`
- **Cursor:** `.cursor-plugin/`, `.cursor/rules/app-teardown.mdc` ve `.mcp.json` hazırdır.
- **MCP Sunucusu:** `python -m app_teardown.mcp_server` ile 9 MCP aracı stdio üzerinden açılır.

## Temel CLI Kullanımı

```powershell
# 0. Fikri analiz et, teknoloji seçeneklerini ve domain konularını gör
.\.venv\Scripts\python.exe -m app_teardown.cli plan-idea "kapılardan geçtiğin yemek yapma oyunu istiyorum hypercasual hamburger"

# 1. En popüler 5 rakibi mağazalarda önizle
.\.venv\Scripts\python.exe -m app_teardown.cli discover "hypercasual runner stack gate" --stores both --country us --lang en --limit 5

# 2. Tam ürün teardown'ı çalıştır (Godot + YouTube kareleri + HEX palet + domain + ücretsiz kitler + blueprint)
.\.venv\Scripts\python.exe -m app_teardown.cli teardown `
  --idea "kapılardan geçtiğin yemek yapma oyunu istiyorum hypercasual hamburger" `
  --tech godot `
  --stores both `
  --mode game `
  --limit 5 `
  --name "hypercasual-burger-gate-godot"

# 3. Ayrı domain araştırması ve ücretsiz asset kit taraması
.\.venv\Scripts\python.exe -m app_teardown.cli research-domain "classic hamburger layers assembly order" "fast food burger ingredients"
.\.venv\Scripts\python.exe -m app_teardown.cli find-kits --mode game --tech godot --theme "burger cooking food"

# 4. Tek bir YouTube videosundan kare ve renk paleti çıkar
.\.venv\Scripts\python.exe -m app_teardown.cli extract-video "https://www.youtube.com/watch?v=..." --out "teardowns/tek-video"

# 5. Mevcut kampanyanın rapor ve dashboard'unu yeniden üret
.\.venv\Scripts\python.exe -m app_teardown.cli rebuild "teardowns/<kampanya_klasoru>"
```

## Lisans

[MIT](../../LICENSE)
