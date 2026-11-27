<div align="center">

# App & Game Teardown Research Toolkit

**Análise competitiva local de apps e jogos móveis para agentes de código AI. Escolha sua stack (Godot, Unity, Flutter, React Native), desmonte o Top 5 na App Store e Google Play quadro a quadro via YouTube, pesquise regras reais do domínio, reúna kits grátis CC0 de UI/UX, 3D e SFX, e gere um blueprint pronto para produção.**

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

- **Planejamento da ideia, escolha de tecnologia e separação mecânica/domínio (`plan-idea`):** Sugere 3 stacks (Godot 4, Unity 6, Phaser ou Flutter, React Native, Native) para você decidir antes de codar. Separa rivais por mecânica da pesquisa real do tema em `DOMAIN_ARASTIRMASI.md`.
- **Kits gratuitos de UI/UX, modelos 3D/2D, áudio e SDKs (`find-kits`):** Reúne recursos `CC0`, `MIT` e `SIL OFL` (Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat) em `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Descoberta Top 5 nas duas lojas (sem API keys):** Pesquisa no Google Play e Apple App Store com preços de IAP, anúncios e avaliações reais.
- **YouTube, extração híbrida de quadros e paletas HEX (`yt-dlp` + `FFmpeg` + `Pillow`):** Baixa os primeiros 4 minutos de gameplay ou walkthrough, extrai 24 quadros, gera storyboards 3x4 e `color_palette_card.png`.
- **Relatórios, blueprint e painel local (`dashboard.html`):** Gera `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md`, `evidence.json` e painel local seguro.

## Instalação rápida

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Licença

[MIT](../../LICENSE)
