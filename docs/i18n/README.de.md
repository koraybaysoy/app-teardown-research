<div align="center">

# App & Game Teardown Research Toolkit

**Lokales Wettbewerbs-Teardown-Toolkit für mobile Apps und Spiele mit AI-Coding-Agents. Wähle deinen Tech-Stack (Godot, Unity, Flutter, React Native), zerlege die Top 5 im App Store und bei Google Play Bild für Bild per YouTube-Gameplay, recherchiere Domänenwissen, sammle kostenlose CC0 UI/UX-, 3D- und SFX-Kits und erstelle einen umsetzbaren Design-Blueprint.**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.ja.md">日本語</a> ·
  <strong>Deutsch</strong> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## Funktionsumfang

- **Ideen-Intake, Tech-Berater und Trennung von Mechanik und Domäne (`plan-idea`):** Vergleicht 3 Stacks (Godot 4, Unity 6, Phaser oder Flutter, React Native, Native) vor dem Start. Trennt die Mechanik-Konkurrenzanalyse von realem Fachwissen in `DOMAIN_ARASTIRMASI.md`.
- **Kostenlose UI/UX-, 3D/2D-, Audio- und SDK-Kits (`find-kits`):** Sammelt geprüfte `CC0`-, `MIT`- und `SIL OFL`-Pakete (Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat) in `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Top-5-Suche in beiden Stores (ohne API-Keys):** Durchsucht Google Play und Apple App Store nach Popularität, IAP-Staffeln, Werbung und Nutzerbewertungen.
- **YouTube-Clip, hybride Frame-Extraktion und HEX-Paletten (`yt-dlp` + `FFmpeg` + `Pillow`):** Lädt die ersten 4 Minuten herunter, extrahiert 24 Keyframes und erstellt 3x4-Storyboards sowie `color_palette_card.png`.
- **Berichte, Design-Blueprint und lokales Studio (`dashboard.html`):** Erzeugt `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md`, `evidence.json` und ein CSP-gehärtetes Dashboard.

## Schnellstart

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Lizenz

[MIT](../../LICENSE)
