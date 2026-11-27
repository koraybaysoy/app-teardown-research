<div align="center">

# App & Game Teardown Research Toolkit

**모바일 앱·게임 설계 전 경쟁작 분해 툴킷: App Store·Google Play 인기 Top 5 발굴, YouTube 게임플레이/워크스루 프레임별 추출, HEX 컬러 팔레트 카드, 웹 근거 아카이빙 및 제품 설계 블루프린트.**

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

- **양대 스토어 인기 Top 5 발굴 (API 키 불필요):** Google Play와 Apple App Store에서 인기 경쟁작을 찾아 IAP 가격표, 광고 여부, 사용자 리뷰를 수집합니다.
- **YouTube 게임플레이·앱 투어 수집 (`yt-dlp`):** 게임 모드에서는 무해설 모바일 게임플레이, 앱 모드에서는 UI/온보딩 투어 영상을 자동 검색해 초반 4분 클립을 안전하게 내려받습니다.
- **하이브리드 프레임 추출 및 컬러 팔레트 (`FFmpeg` + `Pillow`):** 장면 전환 감지와 균등 간격 샘플링으로 24개 프레임을 추출하고, 타임스탬프 스토리보드와 **`color_palette_card.png`** 를 생성합니다.
- **게임·일반 앱 듀얼 분해 루브릭:** UI/UX 배치, 코어 루프와 조작감, 색상 체계, 시각적 훅, 광고·IAP/페이월 배치, 리텐션 루프, 수익화 전략을 체계적으로 분석합니다.
- **웹 근거 아카이브 및 로컬 대시보드 (`dashboard.html`):** `evidence.json`, `teardown_report.md`, `GENEL_TEARDOWN_RAPORU.md`, `TASARIM_BLUEPRINT.md` 및 엄격한 CSP가 적용된 로컬 스튜디오를 생성합니다.

## 빠른 설치

```bash
npx skills add https://github.com/koraybaysoy/app-teardown-research
git clone https://github.com/koraybaysoy/app-teardown-research.git
cd app-teardown-research
bash ./setup.sh   # Windows: .\setup.ps1
```

## 라이선스

[MIT](../../LICENSE)
