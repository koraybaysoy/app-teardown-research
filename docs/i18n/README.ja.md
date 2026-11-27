<div align="center">

# App & Game Teardown Research Toolkit

**モバイルアプリ・ゲーム設計前の競合分解ツールキット：App Store・Google Play 上位5件の抽出、YouTube ゲームプレイ/UIウォークスルーのフレーム分解、HEXカラーパレット生成、Web根拠アーカイブ、設計ブループリント作成。**

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

- **両ストア人気トップ5発見（APIキー不要）：** Google Play と Apple App Store から人気競合を抽出し、IAP価格帯・広告フラグ・ユーザーレビューを取得します。
- **YouTube 実機プレイ＆UIツアー取得（`yt-dlp`）：** ゲームモードでは実況なしゲームプレイ、アプリモードではUI/オンボーディング動画を自動検索し、冒頭4分を安全にダウンロードします。
- **ハイブリッド・フレーム抽出＆配色解析（`FFmpeg` + `Pillow`）：** シーン変化検出と等間隔サンプリングで24フレームを抽出し、タイムスタンプ付きストーリーボードと **`color_palette_card.png`** を生成します。
- **ゲーム＆一般アプリ両対応の分解フレームワーク：** UI/UX配置、コアループと操作感、配色、目を引くフック、広告・IAP/ペイウォール設計、リテンション施策、収益戦略を網羅します。
- **Web根拠アーカイブ＆ローカルダッシュボード（`dashboard.html`）：** `evidence.json`、`teardown_report.md`、`GENEL_TEARDOWN_RAPORU.md`、`TASARIM_BLUEPRINT.md`、厳格CSP対応のローカルスタジオを出力します。

## クイックセットアップ

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## ライセンス

[MIT](../../LICENSE)
