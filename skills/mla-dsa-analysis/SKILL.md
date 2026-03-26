---
name: mla-dsa-analysis
description: "DeepSeek MLA/DSA 프레임워크 기반 정보 분석·의사결정·프레젠테이션 스킬. 디자인: CUFA프레젠테이션(큰글씨72/56/40/32px, #0D0D1A배경, #7C6AF7보라) + PalantirGotham(절제된애니메이션, 지도, 선그래프) + MLA-DSA(데이터밀도, 클릭→상세, 차원카드). 7:2:1색상원칙. 박스나열금지→아키텍처형직관적구조. 네온/이모지/불필요영어 금지. 트리거: '옵션 비교', '선택지 정리', '우선순위', 'MLA DSA', '슬라이드', '발표 자료', '팀 브리핑', '현황 정리', '비교 분석'. 산출물: 다크테마 인터랙티브 HTML(.html) 16:10 풀스크린."
---

# MLA-DSA 분석 스킬 v2

## 1. 디자인 철학: CUFA × Gotham × MLA-DSA

세 DNA의 교차점:
- CUFA: 큰 글씨(title72/big56/mid40/body32/note28), Noto Sans KR, 깔끔한 임팩트
- Palantir Gotham: 절제된 다크UI, 지도시각화, 선그래프, 미묘한 애니메이션, 직관적
- MLA-DSA: 정보 꽉 채움, 클릭→상세, 차원카드, 체인/플로우, 점수시스템

### 절대 원칙
1. 7:2:1 색상: 70% 다크배경(#0D0D1A) / 20% 화이트텍스트 / 10% 액센트(#7C6AF7)
2. 박스나열 금지 → 아키텍처형 직관적 구조(플로우, 지도, 그래프)
3. 네온사인·유치한이모지·불필요영어 금지
4. 설명 부실 금지 — 초보자도 단계별 이해 가능해야 함
5. 콘텐츠는 화면 꽉 채우되 가운데 정렬
6. 지도·선그래프 적극 활용
7. 애니메이션은 Palantir수준 — fadeIn, 카운트업, 라인드로우. 절대 과하지 않게.
8. 글씨는 항상 크게. 최소 note 28px. 22px 이하 금지 (출처 16px만 예외).

### 금지 목록
- 네온 글로우, 그라디언트 배경, 과다한 그림자
- 유치한 이모지 (✨🎯🚀 등)
- 동일 크기 박스 5개 이상 나열
- 내용 없이 큰 글씨만 있는 슬라이드
- 설명 없이 숫자만 던지기
- 22px 이하 텍스트 (출처/페이지번호 외)

## 2. 색상 시스템

```css
:root {
  --bg: #0D0D1A;       /* 깊은 네이비 */
  --purple: #7C6AF7;    /* CUFA 액센트 */
  --white: #FFFFFF;
  --red: #FF4D4D;       /* 위험/부정 */
  --green: #00E09E;     /* 성공/긍정 */
  --amber: #FFB84D;     /* 경고/주의 */
  --blue: #4A9EFF;      /* 정보/중립 */
}
```

카드: rgba(color, 0.08~0.12) 배경 + 2px solid color 테두리
- card-p(보라), card-r(빨강), card-g(초록), card-a(주황)

## 3. 타이포그래피

```css
/* Google Fonts: Noto Sans KR 400,700,900 */
.title { font-size:72px; font-weight:900; line-height:1.15; }
.big   { font-size:56px; font-weight:900; line-height:1.25; }
.mid   { font-size:40px; font-weight:700; line-height:1.4; }
.body  { font-size:32px; font-weight:400; line-height:1.6; }
.note  { font-size:28px; font-weight:400; line-height:1.6; opacity:0.8; }
.label { font-size:22px; font-weight:700; color:var(--purple); letter-spacing:3px; }
```

## 4. 레이아웃

- 슬라이드: 16:10 비율 (width:100vw; height:62.5vw; max-height:100vh)
- 패딩: 80px 100px 50px
- topbar: 6px var(--purple)
- topbar-text: 좌 "CUFA" / 우 "섹션명"
- 프로그레스: 하단 4px 보라
- 네비: ←→키, 스와이프, F=풀스크린

## 5. 슬라이드 타입

A. 임팩트 (bg-purple/bg-red): 중앙, 큰제목, 섹션전환/결론
B. 데이터 (bg-dark): topbar+label+테이블/카드/플로우
C. 지도 (bg-dark): SVG 지도+루트+마커
D. 그래프 (bg-dark): Canvas/SVG 선그래프/바차트

## 6. 애니메이션 (Palantir 수준)

- fadeIn: opacity 0→1 + translateY 8px→0 (0.4s)
- 숫자 카운트업: JS setInterval, 16ms 간격
- 라인 드로우: stroke-dashoffset 애니메이션
- 호버: 보라 테두리 + 미묘한 밝기 증가
- 규칙: prefers-reduced-motion 존중, 1~2초 이내

## 7. 지도 시각화

3가지 유형:
1. 해협/봉쇄: 호르무즈, 수에즈, 말라카 초크포인트
2. 전체 루트: 중동→인도양→한국 에너지 수송
3. 수입 구성: 원유탱커, LNG선, 나프타 등 범례

SVG viewBox 1000×500, 대륙 실루엣 + 해상 루트(곡선, 점선 애니메이션) + 마커

## 8. MLA-DSA 분석 워크플로우

Step 1: 입력 분석 (대상, 제약, 성공기준)
Step 2: MLA 차원 압축 (5~15개, 점수 0~100)
Step 3: DSA 쿼리별 어텐션 (방어체인 시각화)
Step 4: 시각화 선택 (지도/그래프/테이블/플로우/매트릭스)
Step 5: FlashMLA 실행계획 (팀배분, 타임라인)
Step 6: 결론 (임팩트 슬라이드)

## 9. HTML 필수 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>제목</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>/* 색상+타이포+레이아웃+카드+테이블+플로우+애니메이션 */</style>
</head>
<body>
<!-- 슬라이드들: .slide .active bg-dark/bg-purple/bg-red -->
<div class="progress" id="progress"></div>
<div class="sn" id="sn">1/N</div>
<script>/* ←→키, 스와이프, F풀스크린 */</script>
</body>
</html>
```

외부 라이브러리: Google Fonts만. 나머지 순수 HTML/CSS/JS.
파일: /mnt/user-data/outputs/{주제}_슬라이드.html → present_files 전달.
