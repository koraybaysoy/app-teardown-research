<div align="center">

# App & Game Teardown Research Toolkit

**Lokales Wettbewerbs-Teardown-Toolkit für mobile Apps und Spiele mit AI-Coding-Agents. Wähle deinen Tech-Stack (Godot, Unity, Flutter, React Native), zerlege die Top 5 im App Store und bei Google Play Bild für Bild per YouTube-Gameplay, recherchiere reale Themen inklusive Marken-Referenzfotos und Schicht-Anatomie, sammle kostenlose CC0 UI/UX-, 3D- und SFX-Kits, baue nach Rückfrage einen Prototyp und erstelle nach deinem Feedback die fertige Vollversion.**

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

- **Ideen-Intake, Tech-Berater und Trennung von Mechanik und Thema (`plan-idea`):** Vergleicht 3 Stacks (Godot 4, Unity 6, Phaser oder Flutter, React Native, Native) vor dem Start. Trennt die Mechanik-Konkurrenzanalyse von der realen Themen- und Markenrecherche.
- **Reale Themen- und Marken-Referenz-Engine (`research-domain`):** Sammelt Definitionen, Herstellungsprozesse, Schichten/Anatomie und bekannte Marken (Wikipedia + DuckDuckGo) in `DOMAIN_ARASTIRMASI.md`, lädt passende Referenzfotos herunter und erstellt `domain_reference_sheet.png` sowie `domain_palette_card.png`.
- **Kostenlose UI/UX-, 3D/2D-, Audio- und SDK-Kits (`find-kits`):** Sammelt geprüfte `CC0`-, `MIT`- und `SIL OFL`-Pakete (Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat) in `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Top-5-Suche in beiden Stores (ohne API-Keys):** Durchsucht Google Play und Apple App Store nach Popularität, IAP-Staffeln, Werbung und anonymisierten Nutzerbewertungen.
- **YouTube-Clip, hybride Frame-Extraktion und HEX-Paletten (`yt-dlp` + `FFmpeg` + `Pillow`):** Lädt die ersten 4 Minuten herunter, extrahiert 24 Keyframes und erstellt 3x4-Storyboards sowie `color_palette_card.png`.
- **Prototyp-Gate, Feedback und Vollversion (`PROTOTIP_VE_TAM_SURUM_PLANI.md`):** Fragt nach allen Berichten zuerst nach einem schnellen Prototyp, zeigt den Unterschied zur Vollversion, sammelt dein Feedback und baut erst nach deiner Freigabe die komplette App oder das Spiel.
- **Compliance-Modus und Medienbereinigung (`--official-only`, `purge-media`):** Beschränkt Anfragen optional auf offizielle/offen lizenzierte APIs (Apple iTunes, Wikipedia, Wikimedia Commons, Openverse), beachtet `robots.txt` und entfernt heruntergeladene Drittanbieter-Medien bei Erhalt aller Markdown-Berichte.

## Schnellstart

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Lizenz

[MIT](../../LICENSE)
