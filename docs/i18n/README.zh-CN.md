<div align="center">

# App & Game Teardown Research Toolkit

**面向 AI 编程代理的移动应用与游戏立项前竞品分析工具。先选择技术栈（Godot、Unity、Flutter、React Native），再从 App Store 与 Google Play 抓取热门前 5 竞品，逐帧拆解 YouTube 实机演示，生成 HEX 配色卡，调研真实领域知识，收集免费 CC0 UI/UX、3D 模型与音效包，并输出可直接落地的设计蓝图。**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <strong>简体中文</strong> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ko.md">한국어</a>
</p>

</div>

---

## 核心功能

- **想法拆解、技术栈建议与领域分离 (`plan-idea`)：** 先对比 3 套技术方案（Godot 4、Unity 6、Phaser 或 Flutter、React Native、Native）供你确认，再将“核心玩法竞品分析”与“真实领域知识调研”（如汉堡分层顺序、烹饪阶段）分开处理，写入 `DOMAIN_ARASTIRMASI.md`。
- **免费 UI/UX、3D/2D 模型、音效与 SDK 套件 (`find-kits`)：** 按所选引擎与主题筛选 `CC0`、`MIT`、`SIL OFL` 免费资源（Kenney、KayKit、Quaternius、Poly Pizza、Game-Icons、Freesound CC0、Godot AdMob、RevenueCat），输出 `FREE_ASSET_VE_KIT_REHBERI.md`。
- **双商店热门前 5 竞品发现（零 API 费用）：** 检索 Google Play 与 Apple App Store，按下载量、评分数与相关性排序，抓取 IAP 价格阶梯、广告标记与 30+ 用户评论。
- **YouTube 实机演示采集与混合逐帧拆解 (`yt-dlp` + `FFmpeg` + `Pillow`)：** 下载前 4 分钟关键流程，结合场景切换与时间间隔提取 24 帧，生成 3x4 故事板与 `color_palette_card.png` HEX 配色卡。
- **报告、设计蓝图与本地看板 (`dashboard.html`)：** 输出带证据编号的 `teardown_report.md`、`GENEL_TEARDOWN_RAPORU.md`、`TASARIM_BLUEPRINT.md` 以及严格 CSP 的本地交互看板。

## 快速安装

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows 请运行 .\setup.ps1
```

## 许可证

[MIT](../../LICENSE)
