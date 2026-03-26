---
name: inline-mla-dsa-widget
description: "대화 중 인라인 위젯(show_widget)으로 MLA/DSA 아키텍처형 분석을 보여주는 스킬. 파일 생성(HTML) 대신 대화 흐름 안에서 즉시 시각화. 트리거: '분석해줘', '비교해줘', '정리해줘', '현황', '브리핑', '옵션 비교', '선택지', '우선순위', '스코어', '평가', '어떤 게 나아', '뭐가 좋아', 'MLA DSA'. 산출물: claude.ai 네이티브 UI 위젯(show_widget)."
---

# 인라인 MLA/DSA 위젯 스킬 v1

## 1. 핵심 원칙

- **파일이 아니라 대화 안에서 보여준다.** HTML 파일 생성(create_file) 대신 show_widget으로 인라인 렌더링.
- **claude.ai 네이티브 UI와 어울리는 플랫/클린 디자인.** 다크 배경 금지. CSS 변수(--color-*) 사용.
- **MLA 차원 압축 → DSA 스파스 어텐션 → 실행 계획** 3단계 구조.
- **sendPrompt() 버튼**으로 다음 액션을 즉시 연결.

## 2. 필수 컴포넌트 (조합해서 사용)

### 2.1 메트릭 카드 (상단 요약)
- 4열 그리드, background-secondary, border-radius-md
- 큰 숫자(24px/500) + 13px 라벨 + 12px 서브텍스트
- 위험/긴급 수치는 color-text-danger

```html
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;">
  <div style="background:var(--color-background-secondary);border-radius:var(--border-radius-md);padding:1rem;">
    <p style="font-size:13px;color:var(--color-text-secondary);margin:0;">라벨</p>
    <p style="font-size:24px;font-weight:500;margin:4px 0 0;">값</p>
    <p style="font-size:12px;color:var(--color-text-info);margin:2px 0 0;">서브</p>
  </div>
</div>
```

### 2.2 MLA 스코어 바 (차원별 점수)
- 카드(border-tertiary) 안에 배치
- 각 차원: 라벨(120px) + 바트랙(flex:1, background-secondary) + 점수(32px)
- 바 색상: success(80+), info(60-79), warning(40-59), danger(<40)
- JS로 width 0% → score% 애니메이션(0.8s)
- 하단에 종합 점수 표시

```html
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
  <span style="width:120px;font-size:13px;color:var(--color-text-secondary);">차원명</span>
  <div style="flex:1;height:20px;background:var(--color-background-secondary);border-radius:var(--border-radius-md);overflow:hidden;">
    <div class="bar-anim" style="height:100%;width:0%;border-radius:var(--border-radius-md);background:var(--color-text-success);opacity:0.3;transition:width 0.8s ease;"></div>
  </div>
  <span style="width:32px;font-size:14px;font-weight:500;text-align:right;">92</span>
</div>
```

### 2.3 플로우 (단계/프로세스)
- flex + gap:8px + flex-wrap:wrap
- 각 단계: padding 8px 14px, border-radius-md, background-info/warning/success
- 화살표: → (color-text-tertiary)

### 2.4 비교 카드 (옵션 비교)
- 3열 그리드, border-tertiary
- 추천 옵션: border 2px solid border-info + 뱃지
- 각 카드: 제목(15px/500) + 설명(13px, text-secondary) + 상태(13px, 컬러)

### 2.5 sendPrompt 버튼
- 다음 액션을 즉시 실행하는 버튼
- 텍스트 끝에 ↗ 화살표 추가
- 복수 버튼은 margin-left: 8px로 간격

## 3. MLA/DSA 워크플로우

### Step 1: 입력 → 차원 추출
- 분석 대상에서 5~10개 평가 차원을 도출
- 각 차원에 0~100 점수 부여
- 점수 근거를 note로 명시

### Step 2: DSA 쿼리별 어텐션
- 사용자의 질문/목적에 따라 어떤 차원이 활성화되는지 표시
- 비교 카드로 옵션별 강약점 시각화
- 추천 옵션에 뱃지 표시

### Step 3: 실행 계획
- 플로우로 단계 시각화
- sendPrompt 버튼으로 다음 턴 연결

## 4. 디자인 규칙

- 다크 배경(#0D0D1A 등) 금지 — claude.ai는 자체 테마가 있으므로 투명 배경 사용
- CSS 변수만 사용 (--color-background-*, --color-text-*, --color-border-*)
- 폰트: 시스템(Anthropic Sans) 그대로. Noto Sans KR import 금지.
- 그라디언트, 그림자, 네온 금지
- 최소 폰트 11px
- 숫자는 반드시 Math.round() 처리
- border는 0.5px solid var(--color-border-tertiary)
- 카드 border-radius: var(--border-radius-lg)
- read_me 모듈: ["interactive"] 호출 후 사용

## 5. 트리거 패턴

다음 키워드가 포함되면 이 스킬 적용:
- 분석, 비교, 평가, 정리, 현황, 브리핑, 스코어
- 옵션, 선택지, 우선순위, 뭐가 나아, 어떤 게 좋아
- MLA, DSA, 아키텍처
- 프로그램 비교, 취업 비교, 기업 비교

## 6. 안티패턴 (하지 말 것)

- show_widget 대신 create_file로 HTML 파일 생성하여 outputs에 넣기
- 텍스트만으로 표 나열 (위젯이 훨씬 효과적)
- 위젯 안에 장문의 설명 텍스트 넣기 (설명은 대화 본문에)
- 6열 이상 그리드 (4열 이하 유지)
- 차원 15개 이상 (7~10개가 최적)
