<div align="center">

# App & Game Teardown Research Toolkit

**Análisis competitivo local de apps y juegos móviles para agentes de código AI. Elige tu stack tecnológico (Godot, Unity, Flutter, React Native), analiza el Top 5 en App Store y Google Play cuadro por cuadro desde YouTube, investiga reglas reales del tema, reúne kits gratuitos CC0 de UI/UX, 3D y SFX, y genera un blueprint listo para construir.**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <strong>Español</strong> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## Qué hace

- **Plan de idea, asesor tecnológico y separación mecánica/dominio (`plan-idea`):** Compara 3 stacks (Godot 4, Unity 6, Phaser o Flutter, React Native, Native) para que elijas primero. Separa la búsqueda de competidores por mecánica de la investigación real del tema (como orden de capas de hamburguesa) en `DOMAIN_ARASTIRMASI.md`.
- **Buscador de kits gratuitos (`find-kits`):** Reúne paquetes `CC0`, `MIT` y `SIL OFL` de UI/UX, modelos 3D/2D, audio SFX, fuentes y SDKs (Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat) en `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Descubrimiento Top 5 en ambas tiendas (sin claves API):** Busca en Google Play y Apple App Store por popularidad, IAP, anuncios y reseñas reales.
- **YouTube, extracción híbrida de fotogramas y paletas HEX (`yt-dlp` + `FFmpeg` + `Pillow`):** Descarga los primeros 4 minutos de gameplay o walkthrough, extrae 24 fotogramas clave, crea storyboards 3x4 y `color_palette_card.png`.
- **Informes, blueprint y panel local (`dashboard.html`):** Genera `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md`, `evidence.json` y un panel local con CSP estricta.

## Instalación rápida

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # En Windows: .\setup.ps1
```

## Licencia

[MIT](../../LICENSE)
