<div align="center">

# App & Game Teardown Research Toolkit

**移动应用与游戏立项前竞品拆解工具：App Store 与 Google Play 热门前 5 发现、YouTube 实机演示/流程逐帧提取、HEX 配色卡、网络证据归档与可执行产品设计蓝图。**

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

- **双商店热门前 5 竞品发现（零 API 费用）：** 同时检索 Google Play 与 Apple App Store，按下载量、评分数与相关性排序，抓取 IAP 价格阶梯、广告标记与用户评论。
- **YouTube 实机演示与界面导览采集（`yt-dlp`）：** 自动匹配无解说手游实机（游戏模式）或应用引导/界面导览视频（应用模式），截取前 4 分钟关键流程。
- **混合逐帧拆解与配色引擎（`FFmpeg` + `Pillow`）：** 结合场景切换检测与等间隔采样（默认每款 24 帧），输出带时间戳的 3x4 故事板与 **`color_palette_card.png`** HEX 配色卡。
- **双模式产品拆解框架（游戏 / 通用应用）：** 全面覆盖 UI/UX 布局、核心玩法循环与手感、配色方向、视觉亮点、内购/付费墙与广告节奏、留存循环与变现策略。
- **网络证据归档与本地可视化工作室（`dashboard.html`）：** 自动归档收入/变现/UX 拆解网页证据，输出 `teardown_report.md`、`GENEL_TEARDOWN_RAPORU.md`、`TASARIM_BLUEPRINT.md` 与零外部 CDN 的交互式本地看板。

## 快速安装

```bash
# 通用 Agent Skills（Antigravity、Claude Code、Codex、Cursor、Copilot）
npx skills add https://github.com/koraybaysoy/app-teardown-research

# 本地环境搭建（需要 Python 3.11+ 与 FFmpeg）
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows 请运行 .\setup.ps1
```

## CLI 示例

```bash
./.venv/bin/python -m app_teardown.cli discover "hypercasual runner" --stores both --limit 5
./.venv/bin/python -m app_teardown.cli teardown --query "hypercasual runner" --stores both --mode game --limit 5 --name "runner-teardown"
```

## 许可证

[MIT](../../LICENSE)
