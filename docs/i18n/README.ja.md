<div align="center">

# App & Game Teardown Research Toolkit

**AIコーディングエージェント向けのモバイルアプリ・ゲーム設計前競合分析ツールキット。技術スタック選定（Godot、Unity、Flutter、React Native）、App Store・Google Play 上位5件のYouTubeフレーム分解、HEXカラーパレット生成、ドメイン知識調査、無料CC0 UI/UX・3D・効果音キット収集、設計ブループリント出力までをローカルで完結します。**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <strong>日本語</strong> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## 主な機能

- **アイデア分解・技術選定・ドメイン調査 (`plan-idea`)：** Godot 4 / Unity 6 / Phaser または Flutter / React Native / Native の3案を比較提示します。競合のメカニクス調査とテーマ固有のドメイン知識（例：ハンバーガーの層順や調理工程）を分けて `DOMAIN_ARASTIRMASI.md` に記録します。
- **無料 UI/UX・3D/2Dモデル・SFX・SDKキット検索 (`find-kits`)：** 選んだ技術とテーマに合う `CC0` / `MIT` / `SIL OFL` 素材（Kenney、KayKit、Quaternius、Poly Pizza、Freesound CC0、Godot AdMob、RevenueCat）を `FREE_ASSET_VE_KIT_REHBERI.md` にまとめます。
- **両ストア人気トップ5発見（APIキー不要）：** Google Play と Apple App Store から競合、IAP価格帯、広告フラグ、レビューを取得します。
- **YouTube実機取得・フレーム抽出・配色解析 (`yt-dlp` + `FFmpeg` + `Pillow`)：** 冒頭4分から24フレームを抽出し、3x4ストーリーボードと `color_palette_card.png` を生成します。
- **レポート・設計ブループリント・ローカルダッシュボード (`dashboard.html`)：** 根拠ID付きの `teardown_report.md`、`GENEL_TEARDOWN_RAPORU.md`、`TASARIM_BLUEPRINT.md` と厳格CSP対応のローカルスタジオを出力します。

## クイックセットアップ

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## ライセンス

[MIT](../../LICENSE)
