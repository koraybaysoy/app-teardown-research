<div align="center">

# App & Game Teardown Research Toolkit

**Análisis competitivo previo al diseño de apps y juegos móviles: descubrimiento del Top 5 en App Store y Google Play, extracción cuadro por cuadro de gameplay en YouTube, tarjetas de paleta HEX, archivo de evidencia web y blueprint de diseño.**

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

- **Descubrimiento Top 5 en ambas tiendas (sin claves API):** Busca en Google Play y Apple App Store priorizando popularidad, escalera de IAP, banderas de anuncios y reseñas de usuarios.
- **Descarga de Gameplay y Walkthrough en YouTube (`yt-dlp`):** Encuentra automáticamente videos de gameplay sin comentarios (Modo Juego) o recorridos de UI/onboarding (Modo App) y descarga los primeros 4 minutos.
- **Extracción híbrida de fotogramas y paletas HEX (`FFmpeg` + `Pillow`):** Combina detección de cambios de escena e intervalos regulares (24 fotogramas por app), generando storyboards 3x4 con marcas de tiempo y **`color_palette_card.png`**.
- **Rúbricas duales (Juegos y Apps generales):** Evalúa arquitectura UI/UX, bucle principal y game feel, paletas de color, ganchos visuales, cadencia de anuncios e IAP/paywalls, retención D1/D7/D30 y estrategia de ingresos.
- **Evidencia web y estudio local (`dashboard.html`):** Archiva citas verificadas en `web_research.md` y `evidence.json`, generando `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md` y un tablero local con CSP estricta.

## Instalación rápida

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # En Windows: .\setup.ps1
```

## Licencia

[MIT](../../LICENSE)
