<div align="center">

# App & Game Teardown Research Toolkit

**AI 코딩 에이전트를 위한 모바일 앱·게임 설계 전 경쟁작 분석 툴킷. 기술 스택(Godot, Unity, Flutter, React Native)을 먼저 고르고, App Store와 Google Play 인기 Top 5를 YouTube 프레임 단위로 분해하며, 도메인 지식 조사와 무료 CC0 UI/UX·3D·효과음 키트 수집, 실행 가능한 설계 블루프린트 작성까지 로컬에서 처리합니다.**

<p>
  <a href="../../README.md">English</a> ·
  <a href="README.tr.md">Türkçe</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.pt-BR.md">Português</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <strong>한국어</strong>
</p>

</div>

---

## 주요 기능

- **아이디어 분해, 기술 스택 제안, 메커닉/도메인 분리 (`plan-idea`):** Godot 4, Unity 6, Phaser 또는 Flutter, React Native, Native 중 3개 옵션을 비교해 선택하도록 돕습니다. 핵심 메커닉 경쟁작 분석과 실제 도메인 지식 조사(예: 버거 레이어 순서)를 분리해 `DOMAIN_ARASTIRMASI.md`에 기록합니다.
- **무료 UI/UX, 3D/2D 모델, SFX, 폰트, SDK 키트 탐색 (`find-kits`):** 선택한 엔진과 테마에 맞는 `CC0`, `MIT`, `SIL OFL` 리소스(Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat)를 `FREE_ASSET_VE_KIT_REHBERI.md`로 정리합니다.
- **양대 스토어 인기 Top 5 발굴 (API 키 불필요):** Google Play와 Apple App Store에서 인기 경쟁작, IAP 가격대, 광고 플래그, 리뷰를 수집합니다.
- **YouTube 클립 수집, 하이브리드 프레임 추출, HEX 팔레트 (`yt-dlp` + `FFmpeg` + `Pillow`):** 초반 4분에서 24개 핵심 프레임을 추출하고 3x4 스토리보드와 `color_palette_card.png`를 만듭니다.
- **리포트, 설계 블루프린트, 로컬 대시보드 (`dashboard.html`):** 근거 ID가 연결된 `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md`, `evidence.json` 및 엄격한 CSP 로컬 대시보드를 제공합니다.

## 빠른 설치

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## 라이선스

[MIT](../../LICENSE)
