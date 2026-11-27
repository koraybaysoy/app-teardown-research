<div align="center">

# App & Game Teardown Research Toolkit

**Wettbewerbs-Teardown vor dem App- und Spiele-Design: Top-5-Suche im App Store & Google Play, YouTube-Gameplay-/Walkthrough-Frame-Extraktion, HEX-Farbpalettenkarten, Web-Beweisarchiv und umsetzbare Produkt-Blueprints.**

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

- **Top-5-Discovery in beiden Stores (ohne API-Keys):** Durchsucht Google Play und Apple App Store nach den beliebtesten Apps, inklusive IAP-Preisstaffeln, Werbe-Flags und Nutzerbewertungen.
- **YouTube-Gameplay- & Walkthrough-Harvester (`yt-dlp`):** Findet automatisch saubere Mobile-Gameplay-Videos (Game Mode) oder UI/Onboarding-Touren (App Mode) und lädt die ersten 4 Minuten herunter.
- **Hybride Frame-Extraktion & HEX-Farbpaletten (`FFmpeg` + `Pillow`):** Kombiniert Szenenwechsel-Erkennung und Zeitintervalle (24 Frames/App) zu 3x4-Storyboards und **`color_palette_card.png`**.
- **Dual-Mode-Teardown-Rubriken (Games & Apps):** Bewertet UI/UX-Layout, Core Loop & Game Feel, Farbpaletten, visuelle Hooks, Werbe-/IAP-/Paywall-Platzierung, Retention-Strategien und Erlösmodelle.
- **Web-Beweisarchiv & lokales Studio (`dashboard.html`):** Erstellt `evidence.json`, `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md` und ein lokales CSP-gehärtetes Dashboard.

## Schnellstart

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Lizenz

[MIT](../../LICENSE)
