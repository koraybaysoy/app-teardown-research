<div align="center">

# App & Game Teardown Research Toolkit

**AI 코딩 에이전트를 위한 모바일 앱·게임 설계 전 경쟁작 분석 툴킷. 기술 스택(Godot, Unity, Flutter, React Native)을 먼저 고르고, App Store와 Google Play 인기 Top 5를 YouTube 프레임 단위로 분해하며, 실제 주제 구조·유명 브랜드 참고 사진 수집, 무료 CC0 UI/UX·3D·효과음 키트 탐색, 프로토타입 검증과 피드백 후 정식 버전 구현까지 로컬에서 처리합니다.**

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

- **아이디어 분해, 기술 스택 제안, 메커닉/주제 분리 (`plan-idea`):** Godot 4, Unity 6, Phaser 또는 Flutter, React Native, Native 중 3개 옵션을 비교해 선택하도록 돕고 핵심 메커닉 경쟁작과 실제 주제 조사를 분리합니다.
- **실제 주제 구조 및 유명 브랜드 시각 참고 엔진 (`research-domain`):** 정의, 제작 과정, 레이어/구조, 유명 브랜드 정보(Wikipedia + DuckDuckGo)를 `DOMAIN_ARASTIRMASI.md`에 정리하고 참고 사진을 내려받아 `domain_reference_sheet.png`와 `domain_palette_card.png`를 생성합니다.
- **무료 UI/UX, 3D/2D 모델, SFX, 폰트, SDK 키트 탐색 (`find-kits`):** 선택한 엔진과 테마에 맞는 `CC0`, `MIT`, `SIL OFL` 리소스(Kenney, KayKit, Quaternius, Poly Pizza, Freesound CC0, Godot AdMob, RevenueCat)를 `FREE_ASSET_VE_KIT_REHBERI.md`로 정리합니다.
- **양대 스토어 인기 Top 5 발굴 (API 키 불필요):** Google Play와 Apple App Store에서 인기 경쟁작, IAP 가격대, 광고 플래그, 익명화 리뷰를 수집합니다.
- **YouTube 클립 수집, 하이브리드 프레임 추출, HEX 팔레트 (`yt-dlp` + `FFmpeg` + `Pillow`):** 초반 4분에서 24개 핵심 프레임을 추출하고 3x4 스토리보드와 `color_palette_card.png`를 만듭니다.
- **프로토타입 -> 피드백 -> 정식 버전 구현 (`PROTOTIP_VE_TAM_SURUM_PLANI.md`):** 리포트 완료 후 빠른 프로토타입 제작 여부를 묻고, 정식 버전 추가 항목을 안내해 피드백을 받은 뒤 승인 시 전체 앱/게임을 구현합니다.
- **공식 API 준수 모드 및 미디어 정리 (`--official-only`, `purge-media`):** Apple iTunes, Wikipedia, Wikimedia Commons, Openverse 공식/오픈 API만 사용하도록 제한하고 `robots.txt`를 준수하며, 작성한 Markdown 리포트만 남기고 외부 미디어를 일괄 삭제합니다.

## 빠른 설치

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## 라이선스

[MIT](../../LICENSE)
