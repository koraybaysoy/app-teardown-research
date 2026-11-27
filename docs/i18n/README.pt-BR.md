<div align="center">

# App & Game Teardown Research Toolkit

**Análise competitiva local de apps e jogos móveis para agentes de código AI. Escolha sua stack (Godot, Unity, Flutter, React Native), desmonte o Top 5 na App Store e Google Play quadro a quadro via YouTube, pesquise o tema real com fotos de marcas famosas e anatomia de camadas, reúna kits grátis CC0 de UI/UX, 3D e SFX, crie um protótipo rápido e avance para a versão completa após seu feedback.**

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

- **Planejamento da ideia, escolha de tecnologia e separação mecânica/domínio (`plan-idea`):** Sugere 3 stacks (Godot 4, Unity 6, Phaser ou Flutter, React Native, Native) para você decidir antes de codar e separa rivais por mecânica da pesquisa real do tema.
- **Pesquisa do tema real e fotos de marcas famosas (`research-domain`):** Coleta o que é, como é feito, camadas/anatomia e marcas icônicas (Wikipedia + DuckDuckGo) em `DOMAIN_ARASTIRMASI.md`, baixa fotos de referência e cria `domain_reference_sheet.png` e `domain_palette_card.png`.
- **Kits gratuitos de UI/UX, modelos 3D/2D, áudio e SDKs (`find-kits`):** Reúne recursos `CC0`, `MIT` e `SIL OFL` (Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat) em `FREE_ASSET_VE_KIT_REHBERI.md`.
- **Descoberta Top 5 nas duas lojas (sem API keys):** Pesquisa no Google Play e Apple App Store com preços de IAP, anúncios e avaliações anonimizadas.
- **YouTube, extração híbrida de quadros e paletas HEX (`yt-dlp` + `FFmpeg` + `Pillow`):** Baixa os primeiros 4 minutos de gameplay ou walkthrough, extrai 24 quadros, gera storyboards 3x4 e `color_palette_card.png`.
- **Fluxo Protótipo -> Feedback -> Versão completa (`PROTOTIP_VE_TAM_SURUM_PLANI.md`):** Após os relatórios pergunta se você quer um protótipo rápido, mostra o que entra na versão final, coleta seu feedback e constrói o app completo só após sua confirmação.
- **Modo oficial e limpeza de mídia (`--official-only`, `purge-media`):** Restringe consultas a APIs oficiais e abertas (Apple iTunes, Wikipedia, Wikimedia Commons, Openverse), respeita `robots.txt` e remove mídias de terceiros preservando seus relatórios Markdown.

## Instalação rápida

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## Licença

[MIT](../../LICENSE)
