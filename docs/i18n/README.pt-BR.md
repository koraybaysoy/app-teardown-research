<div align="center">

# App & Game Teardown Research Toolkit

**Desconstrução competitiva antes de projetar apps e jogos móveis: descoberta do Top 5 na App Store e Google Play, extração quadro a quadro de gameplay no YouTube, cartões de paleta HEX, arquivo de evidências web e blueprint de produto.**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.es.md">Español</a> ·
  <strong>Português</strong> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## O que faz

- **Descoberta Top 5 nas duas lojas (sem API keys):** Pesquisa no Google Play e Apple App Store ranqueando líderes por popularidade, preços de IAP, sinalizadores de anúncios e avaliações reais.
- **Coleta de Gameplay e Walkthrough no YouTube (`yt-dlp`):** Busca automaticamente gameplay mobile sem narração (Modo Jogo) ou tours de UI/onboarding (Modo App) e baixa clipes limitados de 4 minutos.
- **Extração híbrida de quadros e paletas HEX (`FFmpeg` + `Pillow`):** Combina detecção de troca de cena com amostragem temporal (24 quadros/app), criando storyboards 3x4 e **`color_palette_card.png`**.
- **Análise dupla (Jogos e Apps):** Cobre layout UI/UX, core loop e game feel, cores, destaques visuais, posicionamento de anúncios e paywalls/IAP, retenção D1/D7/D30 e estratégia de receita.
- **Evidências web e painel local (`dashboard.html`):** Mantém rastreabilidade completa em `evidence.json`, `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md` e `TASARIM_BLUEPRINT.md`.

## Instalação rápida

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Licença

[MIT](../../LICENSE)
