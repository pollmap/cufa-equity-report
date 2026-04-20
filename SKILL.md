---
name: cufa-equity-report
description: CUFA 가치투자학회 기업분석보고서 표준 스킬 v15.0. 모든 종목에 재사용 가능한 표준화 프로토콜. Phase 0 Pre-flight → Build → Evaluator v2 자동 검증 → Re-rating Note(조건부). 종목별 하드코딩 제거, 상수 레지스트리 + 모듈 아키텍처 기반.
version: 15.0
last_updated: 2026-04-11
status: standardized
---

# CUFA Equity Research Report — SKILL v15.0 (Standardized)

> **v15.0 재설계 원칙**
> 1. **상수화(Constants)** — 모든 임계값·기준치·최소치를 frozen dataclass로. 종목별 하드코딩 금지.
> 2. **모듈화(Modules)** — `preflight/` `config/` `builder/` `evaluator/` `post_processing/` `sections/` 분리.
> 3. **데이터/규칙 분리** — 종목별 수치는 `config.py`, 규칙·프로토콜은 `SKILL.md`.
> 4. **사례 부록화** — 검증 케이스는 Appendix A에 `CASE-{stock_code}-v{N}` 형식으로 모음.
> 5. **버전 분리** — 과거 v10~v14 히스토리는 CHANGELOG(Appendix B)로 분리, 본문은 최신 표준만.

**이전 버전 백업**: `SKILL_legacy_v14_2_backup.md` (2026-04-11 시점 5,268줄 원본)

---

## 목차

| 섹션 | 제목 | 역할 |
|---|---|---|
| **0** | 철학 & 원칙 | 보고서의 존재 이유, 정직성, 할루시네이션 방지 |
| **1** | 표준 상수 레지스트리 | 모든 수치·임계값을 한 곳에 모은 상수 테이블 |
| **2** | 모듈 아키텍처 | `preflight/` `config/` `builder/` `evaluator/` 모듈 구조 |
| **3** | 워크플로우 (Phase 0~7) | Pre-flight → Build → Evaluate → Re-rating(조건부) 파이프라인 |
| **4** | 섹션 표준 | 11섹션 + Re-rating v2 블록의 구조·최소치 |
| **5** | 서술 & 문체 표준 | SMIC 문체(동사/본서/전술한), 볼드-첫문장, 전환어 |
| **6** | 시각화 표준 | 18종 SVG 헬퍼, 금지 패턴, 이미지 사용 규칙 |
| **7** | 밸류에이션 표준 | 방법론 8종 매트릭스, WACC/Reverse DCF/Implied PER |
| **8** | Evaluator v2 | HARD_MIN + SMIC_STYLE + HALLUCINATION 자동 검증 |
| **9** | 산출물 & 엑셀 스키마 | HTML·Excel 16시트·Markdown 3종 |
| **10** | Nexus MCP 통합 | 도구 레지스트리, MCP 클라이언트, Phase 6.5 백테스트 |
| **App.A** | 검증 케이스 아카이브 | 실전 종목별 발견 사항(하드코딩 금지, 사례만 기록) |
| **App.B** | CHANGELOG | v10 → v15 변경 이력 |
| **App.C** | 금지 규칙 모음 | NEVER-DO 리스트 |

---

## 0. 철학 & 원칙

### 0.1. 투자분석의 본질 — 확률적 추론 프레임워크

투자분석 보고서의 목적은 **주가를 맞히는 것이 아니다.** 미래를 정확히 예측하는 마법이 아니라, **확률을 높이는 과학적·통계적·정량적 연구 방법**이다.

- 맞히더라도 벌지 못할 수 있고, 틀리더라도 벌 수 있다.
- 핵심은 **반증 가능성**: 모든 가정은 검증 가능해야 하고, 틀렸을 때 어디서 틀렸는지 추적 가능해야 한다.
- 성공하면 성공의 원인을, 실패하면 실패의 원인을 정량적으로 복기한다.

**모든 주장은 5요건을 충족해야 한다:**
1. 정량적 근거 (뇌피셜 금지)
2. 근거의 출처 (추적 가능성)
3. 반증 조건 (어떤 수치가 나오면 틀린 건지)
4. 확률 표현 (Bull 20~25% / Base 50% / Bear 25~30%)
5. 사후 복기 가능 (엑셀에 모든 가정과 데이터 저장)

### 0.2. 할루시네이션 방지 — 결정론적 숫자 원칙

**LLM은 숫자를 "그럴듯하게" 만들어내는 본능이 있다. 이것이 투자분석에서 가장 위험하다.**

| 숫자 유형 | 반드시 따라야 할 방식 | 금지 |
|---|---|---|
| 과거 실적 | DART/FnGuide 확정값 | AI가 기억에서 꺼내기 |
| 주가/시총 | pykrx/KRX 당일 종가 | "대략 X만원" |
| 베타(β) | KRX/Bloomberg 60M 주간 회귀 | "보통 1.0~1.5" |
| 무위험이자율(Rf) | 국고채 3년물 (ECOS 당일) | "3.5% 정도" |
| ERP | Damodaran 한국 ERP (연간) | "6% 적용" |
| 매출 추정 | P×Q 분해 → 각 변수 근거 명시 | "15% 성장 예상" |
| Target Multiple | Peer 평균/중앙값 + 프리미엄/할인 근거 | "PER 15배 적용" |

**핵심**: AI는 **계산기(calculator)** 처럼 작동해야 한다. 입력값이 확정되면 출력값은 결정론적(deterministic)이어야 한다. AI가 "창의적으로" 숫자를 만드는 순간 보고서는 실패다.

### 0.3. CUFA 리서치의 정체성 — AI 시대에 살아남는 4가지 해자

1. **데이터→판단의 간극을 메우는 능력**: AI는 데이터를 모을 수 있지만, "이 데이터가 이 기업에 무슨 의미인지"를 판단하는 건 사람이다.
2. **반증 가능한 투자 논리**: 모든 가정에 반증 조건을 붙인다. 6개월 후 복기할 때 "어디서 맞았고 어디서 틀렸는지"를 정량적으로 추적 가능.
3. **엑셀 데이터셋의 재사용 가치**: 보고서 HTML은 읽히고 끝이지만, 엑셀은 살아있는 모델이다.
4. **인터랙티브 + 반응형**: PDF는 죽어있다. CUFA의 HTML 보고서는 클릭·민감도 조작·모바일 대응으로 살아있다.

**브랜딩 슬로건**: "모든 숫자에는 출처가 있고, 모든 가정에는 반증 조건이 있다."

### 0.4. 판단 기준 — 모든 요소의 통합 테스트

모든 글자, 모든 차트, 모든 테이블은 **하나의 질문**으로 판단한다:
> "이걸 빼면 독자가 투자 판단을 내리는 데 지장이 있는가?"
> YES → 남긴다. NO → 삭제한다.

**금지**:
- 분량을 위한 분량 ("80K 채우기" 게임 금지)
- 시각화를 위한 시각화 (메시지 없는 예쁜 차트 금지)
- 뻔한 연혁/ESG 일반론/수식어("글로벌 리딩")

---

## 1. 표준 상수 레지스트리

**원칙**: 모든 임계값·기준치·최소치는 본 섹션의 상수를 참조한다. 종목별로 임계값을 바꾸려면 `XxxThresholds`를 상속해서 오버라이드.

### 1.1. Pre-flight Thresholds (`preflight/thresholds.py`)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PreflightThresholds:
    # 재무 검증
    FINANCIAL_DRIFT_MAX: float = 0.10       # 빌더 vs 실데이터 괴리 한계
    OP_INCOME_SIGN_CHECK: bool = True       # 영업손익 부호 반전 시 STOP

    # 주가 검증
    PRICE_DRIFT_MAX: float = 0.10           # 현재가 vs 빌더 괴리 한계
    VOLATILITY_RERATING_TRIGGER: float = 0.30  # 1년 수익률 절대값 초과 시 Re-rating Mode

    # 삼각검증
    SELF_CONSISTENCY_TOLERANCE: float = 0.01  # PBR × BPS = Price 정합성

    # 데이터 품질
    MIN_YEARS_ACTUAL: int = 3               # 최소 실적 연도
    MIN_DAYS_OHLCV: int = 200               # 최소 주가 거래일 수
    REQUIRE_RAW_ARCHIVE: bool = True        # data/raw/ 원본 보존 필수

PREFLIGHT = PreflightThresholds()
```

### 1.2. Evaluator v2 Criteria (`evaluator/criteria.py`)

```python
@dataclass(frozen=True)
class EvaluatorCriteria:
    # HARD_MIN (필수 통과)
    TEXT_MIN: int = 80_000                  # 본문 문자수
    SVG_MIN: int = 25                       # 차트 개수
    TABLE_MIN: int = 25                     # 테이블 개수
    H2H3_MIN: int = 20                      # 섹션/소제목 개수
    COUNTER_ARG_MIN: int = 3                # 반론 선제 논파 블록
    APPENDIX_MIN: int = 16                  # Appendix 테이블 개수
    REQUIRE_COMPLIANCE: bool = True
    REQUIRE_AI_WATERMARK: bool = True
    REQUIRE_FOOTBALL_FIELD: bool = True
    REQUIRE_SENSITIVITY: bool = True

    # SMIC_STYLE (문체)
    BOLD_FIRST_MIN: int = 150               # <p><strong>첫문장</strong> 패턴 개수
    TRANSITIONS_MIN: int = 30               # 전환어 빈도
    DONGSA_MIN: int = 40                    # "동사" 사용 빈도
    DONGSA_MAX: int = 200                   # 남용 방지 상한
    BONSEO_MIN: int = 5                     # "본서는/본서에서" 빈도
    JEONSUL_MIN: int = 5                    # "전술한/전술했" 빈도
    AVG_PARA_MIN: int = 150                 # 문단 평균 자수 하한
    AVG_PARA_MAX: int = 450                 # 문단 평균 자수 상한

    # HALLUCINATION 탐지
    HALLUCINATION_PATTERNS: tuple = (
        r"약 \d+%", r"대략 \d+", r"정도로? 추정",
        r"일반적으로 \d+", r"보통 \d+", r"통상적으로", r"업계 평균 \d+",
    )

EVAL = EvaluatorCriteria()
```

### 1.3. Section Minima (`sections/minima.py`)

각 섹션의 최소 자수·SVG·테이블·사이드바 개수. 이 기준 미달 시 Evaluator 경고.

```python
@dataclass(frozen=True)
class SectionMinimum:
    chars: int
    svg: int
    tables: int
    sidebars: int

SECTION_MINIMA: dict[str, SectionMinimum] = {
    "main_idea":       SectionMinimum(chars=500,    svg=1, tables=1, sidebars=0),
    "stock_analysis":  SectionMinimum(chars=3_000,  svg=2, tables=1, sidebars=3),
    "company":         SectionMinimum(chars=3_000,  svg=2, tables=1, sidebars=3),
    "industry":        SectionMinimum(chars=10_000, svg=8, tables=3, sidebars=10),
    "company_deep":    SectionMinimum(chars=8_000,  svg=5, tables=2, sidebars=8),
    "ip1":             SectionMinimum(chars=5_000,  svg=3, tables=1, sidebars=5),
    "ip2":             SectionMinimum(chars=5_000,  svg=3, tables=1, sidebars=5),
    "ip3":             SectionMinimum(chars=4_000,  svg=2, tables=1, sidebars=4),
    "financial":       SectionMinimum(chars=6_000,  svg=4, tables=3, sidebars=6),
    "peer":            SectionMinimum(chars=4_000,  svg=3, tables=2, sidebars=4),
    "estimate":        SectionMinimum(chars=6_000,  svg=4, tables=3, sidebars=6),
    "valuation":       SectionMinimum(chars=5_000,  svg=6, tables=3, sidebars=5),
    "risk":            SectionMinimum(chars=4_000,  svg=2, tables=2, sidebars=4),
    "appendix":        SectionMinimum(chars=5_000,  svg=2, tables=16, sidebars=0),
}
# 합계 최소: 본문 63.5K자 + SVG 42 + 테이블 38
```

### 1.4. Industry Checklist Registry (`preflight/industry_checklist.py`)

업종별 "반드시 확인할 데이터" 목록. 종목의 `config.INDUSTRY` 값으로 로드.

```python
INDUSTRY_CHECKLIST: dict[str, tuple[str, ...]] = {
    "해운": (
        "선대 목록(선명/선종/톤수/건조연도)",
        "주요 항로 + 항로별 지정학 리스크",
        "COA vs 스팟 비중",
        "운임 지수(BDI/Baltic LPG/BCTI)",
        "벙커유 연료비 민감도",
        "선박 발주/인도 스케줄",
        "톤마일 분석",
    ),
    "건설": (
        "공장/생산거점 + CAPA + 가동률",
        "수주잔고 상세 (발주처/금액/기간/공정률)",
        "매출인식 타이밍 (공정률 기준)",
        "PF 보증 규모 vs 자기자본",
        "해외 프로젝트 환율·정치 리스크",
        "주택/인프라/플랜트 비중",
        "원가변동 클레임 이력",
    ),
    "제조": (
        "공장별 CAPA 및 가동률",
        "주요 원재료 + 공급처 + 가격 동향",
        "주요 고객사 매출 비중",
        "기술 특허/R&D 투자",
        "환율 민감도 (수출 비중)",
    ),
    "금융": (
        "여신/자산 포트폴리오 구성",
        "NIM/수수료율 추이",
        "자본적정성 (BIS/NCR)",
        "부실채권비율 (NPL ratio)",
        "금리 민감도 분석",
    ),
    "바이오": (
        "파이프라인 전수 목록 (적응증/임상단계/성공확률)",
        "특허 만료 일정",
        "FDA/식약처 허가 타임라인",
        "CMO/CDMO 계약",
        "현금 소진율(Burn Rate)",
    ),
    "IT/플랫폼": (
        "MAU/DAU/ARPU 추이",
        "고객 해지율 (Churn)",
        "Take Rate 변동",
        "클라우드/인프라 비용",
        "경쟁 플랫폼 포지셔닝",
    ),
}
```

### 1.5. Design Tokens (`builder/design_tokens.py`)

```python
# CSS 변수 (단일 표준, 절대 수정 금지)
CSS_VARS = {
    "bg": "#0a0a0a",
    "surface": "#0f0f0f",
    "surface2": "#141414",
    "border": "#222222",
    "purple": "#7c6af7",           # 브랜드 primary
    "purple_light": "#a78bfa",
    "blue": "#6cb4ee",              # Peer/보조
    "positive": "#4ecdc4",          # 상승/Beat
    "negative": "#ff6b6b",          # 하락/Miss
    "amber": "#ffd93d",             # 경고/Re-rating
    "text": "#e0e0e0",
    "text_sec": "#888888",
}

CHART_COLOR_ROLES = {
    "actual": CSS_VARS["purple"],           # 실적(불투명)
    "estimate": CSS_VARS["purple_light"],   # 추정(빗금)
    "peer": CSS_VARS["blue"],
    "positive": CSS_VARS["positive"],
    "negative": CSS_VARS["negative"],
    "warning": CSS_VARS["amber"],
}

BORDER_RADIUS = 4         # 절대 8px 금지
FONT_FAMILY = "'Noto Sans KR', '맑은 고딕', 'Malgun Gothic', sans-serif"
```

### 1.6. 임계값 변경 정책

- **기본 상수 수정 금지**. 종목별 특이치가 필요하면 상속 후 오버라이드:
  ```python
  @dataclass(frozen=True)
  class BioPreflightThresholds(PreflightThresholds):
      MIN_YEARS_ACTUAL: int = 2  # 바이오 신생기업은 3년 실적 없을 수 있음
  ```
- 변경 시 CHANGELOG에 근거 명시 필수.

---

## 2. 모듈 아키텍처

### 2.1. 디렉토리 구조 (표준)

```
cufa-equity-report/               ← 스킬 루트
├── SKILL.md                      ← 본 문서 (규칙·프로토콜)
├── SKILL_legacy_v14_2_backup.md  ← v14.2 이전 버전 백업
├── CHANGELOG.md                  ← 버전 변경 이력
│
├── preflight/                    ← Phase 0 검증 모듈
│   ├── thresholds.py             ← PreflightThresholds 상수
│   ├── checker.py                ← preflight_validate() 함수
│   ├── mcp_client.py             ← NexusMCPClient (SSE 헤더, 파싱)
│   ├── dart_parser.py            ← split_cfs_ofs(), get_account_value()
│   ├── tool_schemas.py           ← MCP 도구 인자 레지스트리
│   └── industry_checklist.py     ← INDUSTRY_CHECKLIST
│
├── config/                       ← 종목별 설정 (보고서마다 복사)
│   ├── _template.py              ← 종목 config 템플릿
│   └── {stock_code}.py           ← 실제 종목 config
│
├── builder/                      ← HTML 빌드 엔진
│   ├── core.py                   ← build() 메인 함수
│   ├── helpers.py                ← section_header, sidebar_wrap, table
│   ├── svg.py                    ← 18종 SVG 헬퍼 (svg_bar, svg_line, ...)
│   ├── components.py             ← counter_arg, callout, expand_card, ...
│   ├── design_tokens.py          ← CSS_VARS, CHART_COLOR_ROLES
│   └── css.py                    ← gen_css() - 단일 표준 CSS
│
├── evaluator/                    ← v2 자동 검증
│   ├── criteria.py               ← EvaluatorCriteria 상수
│   ├── hard_min.py               ← HARD_MIN 체크
│   ├── smic_style.py             ← SMIC_STYLE 체크
│   ├── hallucination.py          ← HALLUCINATION 패턴 탐지
│   └── run.py                    ← evaluate() 통합 실행
│
├── post_processing/              ← 빌드 후 HTML 처리
│   ├── smic_injector.py          ← 문체 주입 (동사/본서/전술한)
│   ├── protect_replace.py        ← 보호-치환-복원 패턴
│   └── rerating_note.py          ← Re-rating v2 블록 생성
│
├── sections/                     ← 11섹션 + 특수 섹션
│   ├── minima.py                 ← SectionMinimum 정의
│   ├── section1_company.py       ← 기업개요
│   ├── section2_industry.py      ← 산업분석
│   ├── ...
│   └── section11_appendix.py     ← Appendix
│
└── output/                       ← 생성 결과 (.gitignore)
    ├── {종목명}_CUFA_보고서.html
    ├── {종목명}_CUFA_본문.md
    ├── {종목명}_재무데이터.xlsx
    └── data/raw/                 ← MCP 원본 응답 (출처 추적)
```

### 2.2. 의존성 방향 (Dependency Rule)

```
config → preflight → builder → post_processing → evaluator → output
                          ↓
                       sections (builder의 하위 구성요소)
```

**규칙**: 하위 모듈은 상위 모듈을 import하지 못한다. `preflight`는 `builder`를 모르고, `builder`는 `evaluator`를 모른다.

### 2.3. 종목별 확장 지점

| 확장 포인트 | 파일 | 역할 |
|---|---|---|
| 데이터 | `config/{stock_code}.py` | 종목 수치·Peer·투자포인트 |
| 임계값 오버라이드 | `config/{stock_code}.py` | `CUSTOM_PREFLIGHT = BioPreflightThresholds()` |
| 섹션 커스텀 | `config/{stock_code}_sections.py` | 특정 섹션의 본문 교체 |
| 산업별 체크 | `preflight/industry_checklist.py` | 신규 산업 추가 |

---

## 3. 워크플로우 (Phase 0~7)

### 3.1. 표준 파이프라인

```
Phase 0: Pre-flight 검증            [MCP 실호출, 10~15분]
   ↓
Phase 1: 리서치 + config.py 작성    [30~60분]
   ↓
Phase 2: 엑셀 v1 빌드               [데이터 → xlsx, 15분]
   ↓
Phase 3: 투자포인트 3개 초안         [사용자 승인 게이트]
   ↓
Phase 4: 본문 작성 (sections/)      [60~120분, 서브에이전트 가능]
   ↓
Phase 5: 엑셀 v2 최종 업데이트       [본문 수치 → xlsx 역반영]
   ↓
Phase 6: HTML 빌드 + Evaluator v2   [자동 ALL PASS 루프]
   ↓
Phase 6.5: 백테스트 검증 (선택)     [Nexus backtest_run]
   ↓
Phase 7: 투자 실행 복기 (장기)      [분기별 TP Revision History]
```

**Re-rating 분기**: Phase 0의 `F2_VOLATILITY`(1년 수익률 ±30% 초과) 또는 `F1_SIGN_FLIP`(영업손익 부호 반전) 발생 시 → **Re-rating v2 모드**(섹션 4.3) 전환.

### 3.2. Phase 0 — Pre-flight 5점 체크 (표준)

```
□ ① 재무제표 실시간 검증 [CRITICAL]
   MCP dart_financial_statements 실호출
   Check: |builder - actual| / actual > PREFLIGHT.FINANCIAL_DRIFT_MAX → F1_FINANCIAL_DRIFT
   Check: sign(builder_op) ≠ sign(actual_op) → F1_SIGN_FLIP

□ ② 주가 실시간 검증 [CRITICAL]
   MCP stocks_history 실호출 (start=today-365)
   Check: |builder_price - actual_price| / actual > PREFLIGHT.PRICE_DRIFT_MAX → F2_PRICE_DRIFT
   Flag: |one_year_return| > PREFLIGHT.VOLATILITY_RERATING_TRIGGER → F2_VOLATILITY

□ ③ 삼각검증 (PBR·BPS·Price 정합성) [CRITICAL]
   Check: PBR × BPS ≠ Price (오차 > PREFLIGHT.SELF_CONSISTENCY_TOLERANCE) → F3_TRIPLE_CHECK

□ ④ 원본 응답 파일 보존 [MANDATORY]
   Save: data/raw/{stock_code}_{tool}_{YYYYMMDD}.raw
   Check: REQUIRE_RAW_ARCHIVE && not exists → F4_RAW_MISSING

□ ⑤ 산업 체크리스트 로드
   Check: config.INDUSTRY in INDUSTRY_CHECKLIST → F5_INDUSTRY (누락 시)
```

### 3.3. Pre-flight 실패 대응 매트릭스

| Fail Code | Trigger | 표준 대응 |
|---|---|---|
| `F1_FINANCIAL_DRIFT` | 재무 드리프트 > `FINANCIAL_DRIFT_MAX` | 빌더 수치 → MCP 실데이터 교체, config 재작성, 본문 논지 재검토 |
| `F1_SIGN_FLIP` | 영업손익 부호 반전 | **Kitchen Sinking vs 실적 악화 판정** (섹션 3.4), 적자 해설 블록 추가 |
| `F2_PRICE_DRIFT` | 주가 드리프트 > `PRICE_DRIFT_MAX` | 현재가 갱신 + 모든 상대지표(Upside/Risk-Reward) 재계산 |
| `F2_VOLATILITY` | 1년 수익률 > `VOLATILITY_RERATING_TRIGGER` | **Re-rating v2 모드** 전환 (섹션 4.3) |
| `F3_TRIPLE_CHECK` | PBR × BPS ≠ Price | config 수치 재검증, builder 상수 재입력 |
| `F4_RAW_MISSING` | 원본 응답 미보존 | 즉시 재호출 + 저장 |
| `F5_INDUSTRY` | 산업 체크리스트 항목 누락 | 섹션 1.4 기준 2차 MCP 호출 |

### 3.4. Kitchen Sinking 판정 프레임 (F1_SIGN_FLIP 대응)

대규모 일회성 적자가 "실적 악화"인지 "선제적 손실 인식(Kitchen Sinking)"인지 판정:

| 검증 항목 | Kitchen Sinking 신호 | 실적 악화 신호 |
|---|---|---|
| OCF/NI Ratio | > 1.0 (OCF 건전) | < 0.5 |
| Accruals Ratio | 음수 | 양수 |
| 전년 대비 매출 | 성장 지속 | 감소 |
| 충당금 성격 | 일회성 분류 공시 | 기조적 비용 증가 |
| 익년 가이던스 | 정상화 제시 | 악화 지속 |

→ Kitchen Sinking 판정 시: Phase 0 실데이터 반영 + 섹션6(재무)에 해설 블록 추가, 투자의견은 유지.
→ 실적 악화 판정 시: 투자의견 재검토, Bear Case 확대.

### 3.5. 사용자 승인 게이트 (Phase 3, Phase 6)

- **Phase 3 게이트**: 투자포인트 3개 초안을 사용자에게 보여주고 승인 받은 후 Phase 4 진입.
- **Phase 6 게이트**: Evaluator v2 ALL PASS 후 브라우저 시각 검수 요청.
- **Re-rating 게이트**: Pre-flight에서 F2_VOLATILITY 발견 시 즉시 사용자에게 보고 후 v2 모드 진입 승인.

---

## 4. 섹션 표준

### 4.1. 표준 11섹션 구조

| # | 섹션 | 최소 자수 | 핵심 구성 |
|---|---|:-:|---|
| Cover | 표지 | 500+ | 투자의견/목표가/IS 7열/Key Metrics/Main Idea 3개 |
| TOC | 목차 | - | 앵커 링크 |
| Key Charts | 핵심차트 | - | 2×2 그리드, 메시지당 1차트 |
| Glossary | 용어 | - | 산업 특화 용어 10~15개 |
| 0-1 | 주가분석 | 3,000 | 1년 일봉 + 이벤트 주석 + 구간별 복기 |
| 0-2 | Key Debates | - | Bull vs Bear 대칭 배치 |
| 0-3 | Variant Perception | - | 컨센서스 vs CUFA 괴리 테이블 |
| 1 | 기업개요 | 3,000 | 사업부 구조, 지배구조, MLA 밸류체인 |
| 2 | 산업분석 | 10,000 | 기초→구조→사이클→글로벌 비교→메가트렌드 |
| 2-1 | 기업분석 | 8,000 | 사업부 심층, 해자, 경영진 전략 |
| 3 | IP① | 5,000 | 테제+근거+counter_arg+결론 |
| 4 | IP② | 5,000 | 동일 구조 |
| 5 | IP③ | 4,000 | 동일 구조 |
| 6 | 재무분석 | 6,000 | 듀폰, CF, 운전자본, QoE |
| 7 | Peer 비교 | 4,000 | OPM-PER 산점도, ROE-PBR 회귀 |
| 8 | 실적추정 | 6,000 | P×Q, 원가 Bottom-up, 분기별, 시나리오 |
| 9 | 밸류에이션 | 5,000 | WACC, PER/PBR/DCF, Football, 민감도, Reverse DCF |
| 10 | 리스크 | 4,000 | EPS 민감도, Kill Condition, Catalyst Timeline |
| 11 | Appendix | 5,000 | A-1~A-16 재무/Peer/체크리스트/방법론 |
| Footer | Compliance | - | 보유 여부 테이블, AI 워터마크 |

### 4.2. 섹션 배치 순서 (확정)

```
Cover → TOC → Glossary → Key Charts → Main Idea
→ 주가분석 → Key Debates → Variant Perception
→ 기업개요 → 산업분석 → 기업분석
→ 투자포인트 ①②③
→ 재무분석 → Peer 비교
→ 실적추정 → 밸류에이션
→ 리스크
→ Appendix → Compliance
```

**원칙**: 기업/산업 이해 → 논쟁 구조 → 투자포인트 → 재무/추정/밸류 → 리스크.

### 4.3. Re-rating Note v2 패턴 (조건부, F2_VOLATILITY 또는 F1_SIGN_FLIP 발생 시)

**트리거 조건**:
- Phase 0에서 1년 수익률 > `VOLATILITY_RERATING_TRIGGER` 또는 영업손익 부호 반전
- 기존 빌더/추정치 대비 수치 괴리 > `FINANCIAL_DRIFT_MAX`

**구조**:
```
Cover → [Re-rating Note v2 블록] → 기존 섹션 1~11 → Phase 6.5 → Compliance
```

**Re-rating Note v2 블록 구성 요소** (`post_processing/rerating_note.py`):

```python
def gen_rerating_note_v2(v1_config, v2_config, preflight_result) -> str:
    """
    Args:
        v1_config: 구버전 config (기존 빌더 수치)
        v2_config: 신버전 config (Phase 0 실데이터 반영)
        preflight_result: PreflightResult 객체

    Returns:
        HTML 블록 (커버 직후 삽입용)
    """
    return f'''
    <div class="section" id="rerating_v2">
      <h2>🔔 긴급 재평가 — {preflight_result.fails}</h2>

      1. v1 무효화 경고 박스
         - 발견된 Fail Code 나열
         - v1 가정 vs v2 실데이터 비교

      2. v1 vs v2 하향 테이블 (standardized)
         | 항목 | v1 | v2 | 변화 |
         | 투자의견 | ... | ... | ... |
         | 현재가 | ... | ... | +{변화율}% |
         | 목표주가 | ... | ... | ... |
         | Upside | ... | ... | ... |
         | Risk/Reward | ... | ... | ... |
         | Conviction | ... | ... | ... |

      3. v2 재산정 밸류에이션 (Peer 기반)
         - Peer 평균 Fwd PER 재적용
         - PBR 재계산

      4. 새 투자포인트 3개 (IP Reset)

      5. Bear Case 확대 (확률 25% → 30%+)

      6. Kill Conditions 재정의

      7. 투자자 액션 가이드 (신규/기존/모니터링/재진입)
    </div>
    '''
```

**핵심 원칙**:
- 기존 v1 섹션은 **삭제 금지**, "v1 분석" 배지로 유지 → 반증 가능성 원칙
- v2 블록의 v1 참조 텍스트("v1 BUY → v2 HOLD")는 post-processing 치환에서 **보호 영역**

### 4.4. 섹션별 필수 컴포넌트

각 섹션에 반드시 포함해야 할 컴포넌트 (Evaluator 자동 체크):

| 섹션 | 필수 컴포넌트 |
|---|---|
| 투자포인트 | `counter_arg()` 블록 1건+ |
| 재무분석 | 듀폰 분해 테이블, FCF 추이 |
| Peer 비교 | OPM vs PER 산점도 |
| 실적추정 | ASP 분해 테이블 + 원가 Bottom-up + Bull/Base/Bear |
| 밸류에이션 | Football Field + 민감도 히트맵 + Reverse DCF + Implied PER |
| 리스크 | EPS 민감도 테이블 + Kill Condition 3건+ |
| Appendix | A-1~A-16 (IS/BS/CF/주당/Valuation/Peer/DCF/체크리스트/방법론) |

---

## 5. 서술 & 문체 표준 (SMIC 벤치마크)

### 5.1. 핵심 지칭 원칙

| 패턴 | 빈도 | 용도 | 예시 |
|---|:-:|---|---|
| **동사(同社)는/의** | 40~200회/편 | 분석 대상 기업 기본 호칭 | "동사는 TC2C 공정이 완성될 경우~" |
| **본서는/에서는** | 5~50회/편 | 보고서 자체의 주장 | "본서는 26년까지 유가가~" |
| **전술한/후술할** | 5~30회/편 | 섹션 간 크로스레퍼런스 | "전술한 바와 같이~" |
| 기업명 직접 | 1~2회 | Cover 첫 등장만 예외 | "현대건설(000720, 이하 '동사')" |

### 5.2. 볼드-첫문장 원칙 (150개+)

**모든 단락의 첫 문장은 핵심 주장을 볼드 처리한다.** SMIC 보고서의 핵심 패턴.

```html
<p><strong>정유사는 저질의 정제유를 고품질의 경질유로 바꾸기 위해 고도화 설비 도입을 늘리고 있다.</strong>
고도화 설비란 원유의 잔사유 분획을 경질유 분획으로 전환하는 공정을 말한다. 대표적으로 FCC, 수첨분해(HDC), 코커(Coker) 등이 있으며...</p>
```

**구조**: 볼드 1문장(20~40자) + 일반 3~5문장(150~300자)

### 5.3. 전환어 레지스트리 (30개+ 빈도)

```python
TRANSITION_WORDS = {
    "이전 연결":   ["전술한 바와 같이", "전술했듯이", "앞서 살펴본"],
    "질문→답변":  ["그렇다면", "그런데"],
    "추가":       ["이에 더해", "나아가", "이와 함께"],
    "시각 전환":   ["한편"],
    "소결":       ["이처럼", "이와 같이"],
    "사례":       ["실제로"],
    "리스크 인정": ["다만", "그러나"],
    "상세":       ["구체적으로"],
}
```

**Evaluator**: 본문에서 상기 전환어 총 빈도가 `EVAL.TRANSITIONS_MIN`(30) 미만이면 FAIL.

### 5.4. 추론 체인 4~5단계 (S등급 달성 조건)

| 등급 | 추론 단계 | 패턴 |
|---|---|---|
| B | 2~3단계 | 산업성장 → 매출증가 → 주가상승 |
| A | 3~4단계 | 수요증가 → 매출성장 → OPM개선 → 주가상승 |
| **S** | **4~5단계** | **트렌드 → 구조변화 → 포지셔닝 → 수익영향 → 리레이팅** |

모든 투자포인트는 작성 전에 추론 체인을 설계:
```
IP 추론 체인 설계:
  [1] _____ (거시/산업 트렌드)
  [2] _____ (카테고리 선택 이유)
  [3] _____ (기업 경쟁력/해자)
  [4] _____ (수익 영향 정량화)
  [5] _____ (밸류에이션 임팩트)
```

### 5.5. 2중 반박 구조 (SMIC 핵심)

**방식 1 — 인라인 반박** (IP 본문 내, 필수)
```
"그렇다면 [우려사항]은 없는 것일까?
본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다.
① 공정 구조의 차이 ② 글로벌 공급 과잉 압력 완화 ③ 아람코 전략적 의도"
```

**방식 2 — `counter_arg()` 블록** (섹션 10 리스크, 별도 UI)
- 발생 확률(%) + 완화 요인 + 모니터링 KPI + EPS 영향도(원)

**HARD_MIN**: IP 3개 × 인라인 반박 1건+ = **최소 3건**

### 5.6. 금지 표현 (자동 탐지)

```python
WEAK_ENDINGS = [
    r"할 것으로 기대된다",   # → "~할 것이다" 또는 "~것으로 판단한다"
    r"할 수도 있다",         # → "~할 가능성이 있다(X%)" 또는 삭제
    r"할 것으로 보인다",     # → "~것으로 판단한다"
    r"인 것으로 사료된다",   # → "~이다"
    r"할 것으로 예상된다",   # → "~전망이다"
    r"않을까 싶다",          # 삭제
]

FILLER_WORDS = [
    r"매우",         # → 정량화
    r"상당히",       # → 정량화
    r"흥미로운",     # → 구체적 수치로 대체
    r"주목할 만한",  # → 구체적 수치로 대체
]
```

### 5.7. 사이드바 레이아웃 규칙 (CRITICAL)

**`sidebar_wrap` 안에는 텍스트만. 차트는 밖에.**

```python
# ✅ 올바른 패턴
h += sidebar_wrap(kws, text_content)      # 텍스트만
h += '<div class="chart-pair">'
h += chart_a                              # 차트는 밖
h += chart_b
h += '</div>'

# ❌ 금지 패턴
content = text + chart_html
h += sidebar_wrap(kws, content)           # 그리드 깨짐
```

**사이드바 커버리지 최소 60%**: 섹션의 모든 소제목+본문이 sidebar_wrap 안에 있어야 한다.

---

## 6. 시각화 표준

### 6.1. SVG 헬퍼 카탈로그 (18종, `builder/svg.py`)

| # | 함수 | 용도 |
|---|---|---|
| 1 | `svg_bar()` | 수직 막대 (연도별 실적) |
| 2 | `svg_hbar()` | 수평 막대 (Peer 순위) |
| 3 | `svg_line()` | 라인 차트 (추세) |
| 4 | `svg_area()` | 누적 영역 (구성비 추이) |
| 5 | `svg_donut()` | 도넛 (비중) |
| 6 | `svg_scatter()` | 산점도 (OPM vs PER) |
| 7 | `svg_waterfall()` | 워터폴 (Bridge) |
| 8 | `svg_grouped_bar()` | 그룹 막대 (사업부×연도) |
| 9 | `svg_football()` | Football Field (밸류 범위) |
| 10 | `svg_heatmap()` | 히트맵 (민감도) |
| 11 | `svg_bubble_risk()` | 리스크 매트릭스 |
| 12 | `svg_per_band()` | PER/PBR 밴드 |
| 13 | `svg_flow_diagram()` | 플로우 (밸류체인) |
| 14 | `svg_timeline()` | 타임라인 (Catalyst) |
| 15 | `svg_roe_pbr_path()` | ROE-PBR 경로 |
| 16 | `svg_rebased_price()` | 주가 리베이스 비교 |
| 17 | `svg_comparison_matrix()` | 비교 매트릭스 |
| 18 | `svg_tam_sam_som()` | TAM/SAM/SOM 동심원 |

**절대 금지**: `svg_radar()` — v13부터 완전 금지. 대체: `svg_grouped_bar()` 또는 `svg_scatter()`.

### 6.2. 차트 유형 선택 매트릭스

| 보여줄 것 | 최적 차트 | 금지 |
|---|---|---|
| 연도별 매출(≤6개) | 수직 막대 | 파이 |
| 분기별 추이(7+) | 라인 | 파이 |
| 매출 구성비(3~5) | 도넛 | 3D 파이 |
| 매출+OPM 동시 | 이중축 bar+line | 이중 라인 |
| Peer OPM vs PER | 산점도 | 막대 |
| 비용 분해 | 워터폴 | 파이 |
| DCF 민감도 | 히트맵(숫자 필수) | 막대 |
| 밸류 범위 | Football | 라인 |
| PER Band | 밴드 | 막대 |
| 주가 1년 | 라인 + 거래량 바 | 월봉 |

### 6.3. Y축·추정치·색상 규칙

**Y축**:
- 막대: 0 시작 필수 (절단 금지)
- 라인: 데이터 범위 허용 (시작점 명시)

**추정치 구분**:
- 실적(A): 불투명 100%, 실선
- 추정(E): alpha 0.4 + 빗금 패턴 + 대시 라인

**색상 역할 기반** (`CHART_COLOR_ROLES` 참조):
- 항상 역할(role) 변수 사용, 하드코딩 `#ff0000` 금지
- Positive=틸(`#4ecdc4`), Negative=레드(`#ff6b6b`), Warning=앰버(`#ffd93d`)

### 6.4. 절대 금지 패턴

1. 3D 차트
2. 파이 차트 6개+ 슬라이스
3. 축 라벨 누락
4. 범례 먼 곳 분리 (직접 라벨링)
5. X축 그리드 (Y축만)
6. 무지개 색상
7. 세로 X축 라벨 (수평 막대 전환)
8. 그라데이션 막대
9. 이중축 라인-라인
10. Chartjunk (그림자/3D/아이콘 장식)
11. **svg_radar (v13 이후 완전 금지)**

### 6.5. 이미지 사용 규칙

**허용**:
1. 기업 공식 홈페이지 (로고, 제품, 공장 사진) — 최우선
2. DART IR 자료
3. Wikimedia Commons (CC 라이센스)
4. Google Fonts (`@import url('Noto Sans KR')`)

**금지**:
- Unsplash/Pexels 등 스톡 이미지
- 외부 CDN 스크립트/라이브러리
- 유료 보고서 캡처

**형식**: 모든 이미지는 HTML 단일 파일 유지를 위해 base64 인라인 또는 `data/images/` 저장.

---

## 7. 밸류에이션 표준

### 7.1. 방법론 8종 매트릭스

| 방법론 | 언제 사용 | 언제 부적합 |
|---|---|---|
| Historical PER | 안정적 이익, Peer 존재 | 적자, 사이클 저점 |
| Historical PBR | 자산 중심, 금융업 | 자산 경량, 고성장 |
| EV/EBITDA | 자본집약, 국가 간 비교 | EBITDA 음수 |
| DCF | 장기 성장, Peer 부재 | 3년 미만 영업이력 |
| RIM | 금융업, 안정적 BPS | 자본 변동성, 적자 |
| rNPV | 바이오 파이프라인 | 비제약 기업 |
| SOTP | 다각화 지주사 | 단일 사업 |
| Historical Peer | 현재 Peer 부적합 | 과거 아날로그 없음 |

### 7.2. "Why X? Why not Y?" 필수 블록

모든 밸류에이션 섹션에 반드시 포함:

```python
def valuation_rationale(chosen: str, chosen_reason: str,
                        excluded: list[tuple[str, str]]) -> str:
    """
    Args:
        chosen: 선택 방법론명
        chosen_reason: 선택 근거 3문장
        excluded: [(배제 방법론, 부적합 사유), ...]
    """
```

### 7.3. WACC 산출 표준

```
Rf   = 국고채 3년물 (ECOS 당일)
β    = KRX 60M 주간수익률 회귀 (pykrx)
ERP  = Damodaran 한국 ERP (연간)
Ke   = Rf + β × ERP
Kd   = DART 가중평균 차입금리 × (1 - 법인세율)
WACC = (E/V) × Ke + (D/V) × Kd
     + 산업 리스크 프리미엄 (EPC/원자재/지정학 가산)
```

### 7.4. Reverse DCF (모든 보고서 필수)

```
Step 1: DCF로 목표주가 산출
Step 2: 현재가를 고정 → g_implied 역산
Step 3: 비교 — "시장은 g_implied% 반영, 당사 추정 g%" → 갭이 Upside 근거
Step 4: 밸류에이션 섹션에 한 문단으로 서술
```

**해석**:
- g_implied < 한국 명목GDP 장기 평균(2.5%) → 시장이 비관적 (저평가 가능)
- g_implied > 3.5% → 시장이 낙관적 (고평가 주의)

### 7.5. Implied PER Sanity Check

```
Implied PER = 목표주가 ÷ 터미널연도 EPS
```

| Implied PER | 판정 |
|---|---|
| < 15x | 보수적 (추가 상승 여력) |
| 15~30x | 합리적 |
| 30~40x | 공격적 (근거 보강 필요) |
| **> 40x** | **Red Flag** (성장 가정 재검토) |

### 7.6. 시나리오 확률 가중 TP (표준)

```python
scenarios = [
    {"name": "Bull", "prob": 0.20, "tp": bull_price, "trigger": "..."},
    {"name": "Base", "prob": 0.50, "tp": base_price, "trigger": "..."},
    {"name": "Bear", "prob": 0.30, "tp": bear_price, "trigger": "..."},
]
weighted_tp = sum(s["prob"] * s["tp"] for s in scenarios)
risk_reward = (bull_price - current) / (current - bear_price)
```

**Conviction Level**:
- HIGH: Upside > 30% + R/R > 2.0 + 3개월 내 Catalyst
- MEDIUM: Upside 15~30% + R/R > 1.5
- LOW: Upside < 15% or R/R < 1.5

---

## 8. Evaluator v2 (품질 자동 검증)

### 8.1. 통합 실행 (`evaluator/run.py`)

```python
from evaluator.criteria import EVAL
from evaluator.hard_min import check_hard_min
from evaluator.smic_style import check_smic_style
from evaluator.hallucination import check_hallucination

def evaluate(html: str, section_minima: dict) -> EvaluationResult:
    hard = check_hard_min(html, EVAL)
    smic = check_smic_style(html, EVAL)
    hallu = check_hallucination(html, EVAL)
    sections = check_section_chars(html, section_minima)

    all_checks = {**hard, **smic, **sections}
    passed = sum(1 for ok, _ in all_checks.values() if ok)
    total = len(all_checks)

    return EvaluationResult(
        passed=passed, total=total,
        fails=[msg for ok, msg in all_checks.values() if not ok],
        hallucinations=hallu,
    )
```

### 8.2. HARD_MIN 체크 (14개)

`EVAL.TEXT_MIN`, `SVG_MIN`, `TABLE_MIN`, `H2H3_MIN`, `COUNTER_ARG_MIN` 등을 참조하여 수치 하드코딩 제거.

### 8.3. SMIC_STYLE 체크

- Bold 첫문장 ≥ `EVAL.BOLD_FIRST_MIN`
- 전환어 빈도 ≥ `EVAL.TRANSITIONS_MIN`
- 동사 사용 `EVAL.DONGSA_MIN` ≤ n ≤ `EVAL.DONGSA_MAX`
- 본서는 ≥ `EVAL.BONSEO_MIN`
- 전술한 ≥ `EVAL.JEONSUL_MIN`
- 문단 평균 자수 `EVAL.AVG_PARA_MIN` ≤ n ≤ `EVAL.AVG_PARA_MAX`

### 8.4. HALLUCINATION 탐지

```python
def check_hallucination(html: str, criteria: EvaluatorCriteria) -> list[str]:
    import re
    matches = []
    for pattern in criteria.HALLUCINATION_PATTERNS:
        found = re.findall(pattern, html)
        if found:
            matches.append(f"{pattern}: {found[:5]}")
    return matches
```

### 8.5. 빌드 루프 (자동 재시도)

```python
MAX_ITERATIONS = 3
for i in range(MAX_ITERATIONS):
    html = build(config)
    result = evaluate(html, SECTION_MINIMA)
    if result.passed == result.total:
        break
    print(f"Iteration {i+1}: {result.passed}/{result.total} — {result.fails}")
    # 자동 보강 로직 (optional): fails에 따라 섹션별 내용 추가
```

---

## 9. 산출물 & 엑셀 스키마

### 9.1. 필수 산출물 3종

| 파일 | 용도 | 최소 기준 |
|---|---|---|
| `{종목명}_CUFA_보고서.html` | 인터랙티브 보고서 | 250 KB+, 80K자+, 25 SVG+, 25 테이블+ |
| `{종목명}_CUFA_본문.md` | Phase 1 마크다운 원본 | 60K자+ |
| `{종목명}_재무데이터.xlsx` | Single Source of Truth | 16시트 |

### 9.2. Excel 16시트 표준 스키마

| # | 시트명 | 내용 |
|---|---|---|
| 0 | Cover | 작성자, 투자의견, 시트 맵 |
| 1 | IS_CFS | 연결 손익계산서 (DART 실데이터, 5~7년) |
| 2 | BS_CFS | 연결 재무상태표 |
| 3 | CF_CFS | 연결 현금흐름표 |
| 4 | 원가판관비 | Bottom-up 분해 (자재/노무/외주/간접, 판관비 세부) |
| 5 | 금융손익 | 유효이자율 기반 이자수익/비용 추정 |
| 6 | 법인세 | 유효세율 + 당기순이익 연계 |
| 7 | IS_OFS | 별도 손익계산서 |
| 8 | BS_OFS_CF | 별도 BS + CF 요약 |
| 9 | PxQ | 사업부별 ASP×Q 매출 추정 (5년) |
| 10 | Valuation | WACC 파라미터 + 3종 방법론 + 시나리오 |
| 11 | Peer | 국내·해외 Peer 10+ 비교 |
| 12 | Macro | 금리/환율/GDP/원자재 |
| 13 | Stock_Price | 1년 주가 (실데이터) |
| 14 | PL_시나리오 | Bull/Base/Bear 확률 가중 |
| 15 | **데이터출처** | **모든 수치의 원본 추적 (핵심)** |

**15_데이터출처 시트 구조** (핵심):
| 데이터 항목 | 값 | 출처 | MCP 도구 | 수집일시(KST) | 검증 |
|---|---|---|---|---|---|
| 매출 2024 | ... | DART 사업보고서 | dart_financial_statements | ... | O |
| 현재가 | ... | KRX | stocks_history | ... | O |

### 9.3. HTML 구조 (표준 조립 순서)

```python
# builder/core.py
def build(config) -> str:
    html = _doctype_head(config)
    html += _sticky_bar(config)
    html += gen_cover(config)

    if config.PREFLIGHT_RESULT.is_rerating_mode():
        html += gen_rerating_note_v2(config.v1, config.v2, config.PREFLIGHT_RESULT)

    html += gen_toc(config)
    html += gen_glossary(config)
    html += gen_key_charts(config)
    html += gen_main_idea(config)

    for section in SECTION_ORDER:
        html += globals()[f"gen_{section}"](config)

    html += gen_phase65_backtest(config)  # 선택
    html += gen_compliance(config)
    html += gen_interactive_js()
    html += "</body></html>"

    html = post_processing.smic_inject(html)
    html = post_processing.protect_replace_v2_numbers(html, config)
    return html
```

---

## 10. Nexus MCP 통합

### 10.1. MCP 도구 스키마 레지스트리 (`preflight/tool_schemas.py`)

```python
TOOL_SCHEMAS = {
    "dart_financial_statements": {
        "required": ["stock_code", "year", "report_type"],
        "hints": {
            "stock_code": "6자리 문자열 (ticker 아님)",
            "year": "문자열 '2024'",
            "report_type": "'CFS' or 'OFS' (대문자)",
        },
        "quirks": [
            "IS/BS/CF에 연결+별도 혼재 가능 → ord 필드로 구분",
            "당기순이익(손실) 행 중복 가능 (EPS 계산용 + 총계)",
        ],
    },
    "stocks_history": {
        "required": ["stock_code", "start_date", "end_date"],
        "hints": {
            "stock_code": "6자리 (ticker 아님)",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
        },
    },
    "backtest_run": {
        "required": ["ohlcv_data", "strategy_name"],
        "hints": {
            "ohlcv_data": "list[dict(date, open, high, low, close, volume)]",
            "strategy_name": "내장 6종: RSI_oversold / MACD_crossover / Bollinger_bounce / MA_cross / Mean_reversion / Momentum",
        },
    },
}

def validate_args(tool_name: str, arguments: dict) -> None:
    schema = TOOL_SCHEMAS[tool_name]
    missing = [k for k in schema["required"] if k not in arguments]
    if missing:
        raise ValueError(
            f"{tool_name} 인자 누락: {missing}. 힌트: {schema['hints']}"
        )
```

### 10.2. MCP 클라이언트 (`preflight/mcp_client.py`)

```python
import json, re, subprocess
from typing import Any, Protocol

NEXUS_MCP_URL = "http://<MCP_VPS_HOST>/mcp"
SSE_HEADERS = [
    "-H", "Content-Type: application/json",
    "-H", "Accept: application/json, text/event-stream",  # 필수!
]

class MCPClient(Protocol):
    def call(self, tool_name: str, arguments: dict) -> dict[str, Any]: ...


class NexusMCPClient:
    def __init__(self, url: str = NEXUS_MCP_URL, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self._call_id = 0

    def call(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        from .tool_schemas import validate_args
        validate_args(tool_name, arguments)  # 사전 검증

        self._call_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        proc = subprocess.run(
            ["curl", "-s", "-m", str(self.timeout), self.url, "-X", "POST",
             *SSE_HEADERS, "-d", json.dumps(payload, ensure_ascii=False)],
            capture_output=True, text=True, encoding="utf-8",
        )
        m = re.search(r"data:\s*(\{.*\})", proc.stdout, re.DOTALL)
        if not m:
            raise RuntimeError(f"MCP 응답 파싱 실패: {proc.stdout[:500]}")
        data = json.loads(m.group(1))
        if data.get("result", {}).get("isError"):
            err = data["result"]["content"][0]["text"]
            raise RuntimeError(f"MCP 도구 에러: {err[:500]}")
        inner = json.loads(data["result"]["content"][0]["text"])
        return inner
```

### 10.3. DART 응답 파싱 표준 (`preflight/dart_parser.py`)

```python
def split_cfs_ofs(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """dart_financial_statements 응답을 연결/별도로 분리."""
    def _split_by_sj(sj: str) -> tuple[list, list]:
        rows = sorted(
            [r for r in items if r.get("sj_div") == sj],
            key=lambda x: int(x.get("ord", 0)),
        )
        mid = len(rows) // 2
        return rows[:mid] if mid else rows, rows[mid:] if mid else []

    cfs: list[dict] = []
    ofs: list[dict] = []
    for sj in ("IS", "BS", "CF"):
        c, o = _split_by_sj(sj)
        cfs.extend(c)
        ofs.extend(o)
    return cfs, ofs


def get_account_value(
    rows: list[dict],
    account_name: str,
    period: str = "thstrm",  # thstrm/frmtrm/bfefrmtrm
) -> int:
    for r in rows:
        if r.get("account_nm") == account_name:
            raw = r.get(f"{period}_amount", "0").replace(",", "")
            return int(raw) if raw else 0
    return 0
```

### 10.4. Phase 6.5 백테스트 (`builder/phase65_backtest.py`)

```python
# 백테스트 자동화: IP → 전략 매핑 → 실행 → 블록 생성

IP_TO_STRATEGY = {
    "momentum":      "Momentum",       # 해외 수주·성장 모멘텀
    "breakout":      "MA_cross",       # 재건축·추세 확산
    "mean_reversion": "Mean_reversion",# 저평가 해소
    "rsi_oversold":  "RSI_oversold",
    "macd":          "MACD_crossover",
    "bollinger":     "Bollinger_bounce",
}

def run_phase65(config, mcp: MCPClient) -> dict:
    # 1) 1년 주가 수집
    stock_resp = mcp.call("stocks_history", {
        "stock_code": config.stock_code,
        "start_date": (config.report_date - timedelta(days=365)).isoformat(),
        "end_date": config.report_date.isoformat(),
    })
    ohlcv = [
        {"date": r["date"], "open": r["open"], "high": r["high"],
         "low": r["low"], "close": r["close"], "volume": r["volume"]}
        for r in stock_resp["data"]
    ]

    # 2) IP별 전략 백테스트 (사용자 승인 필수)
    results = {}
    for ip_type, strategy_name in IP_TO_STRATEGY.items():
        if ip_type not in config.ip_strategies:
            continue
        res = mcp.call("backtest_run", {
            "ohlcv_data": ohlcv,
            "strategy_name": strategy_name,
            "initial_capital": 10_000_000,
            "commission": 0.0018,
            "position_size": 0.95,
        })
        results[strategy_name] = res["data"]

    # 3) HTML 블록 생성
    return gen_phase65_block(results, config)
```

### 10.5. Fallback 전략 (KIS → Nexus)

| Primary | Fallback | 조건 |
|---|---|---|
| `kis-backtest` MCP (127.0.0.1:3846) | `nexus-finance` `backtest_run` | 로컬 포트 미기동 시 |
| DART OpenAPI 직접 | `dart_financial_statements` | Nexus MCP 미접속 시 |
| `stocks_history` | `pykrx` 직접 호출 | MCP 응답 실패 시 |

---

## Appendix A. 검증 케이스 아카이브

**규칙**: 새 종목 작성 중 Pre-flight Fail이 발생하면 `CASE-{stock_code}-v{N}` 형식으로 이 표에 추가. **수치 자체는 config.py에 있으므로 여기에 하드코딩하지 않는다.** 기록은 드리프트 %·Fail Code·적용 대응으로만.

| Case ID | 종목 | Fail Codes | 드리프트 규모 | 적용 대응 | 기록일 |
|---|---|---|---|---|---|
| CASE-000720-v2 | 현대건설 | F1_SIGN_FLIP, F1_FINANCIAL_DRIFT, F2_VOLATILITY, F3_TRIPLE_CHECK | 재무 +52%, 주가 +370%, 영업손익 부호 반전 | Re-rating Note v2 모드, BUY→HOLD, 섹션5 전면 재작성, Bear 확률 25→30% | 2026.04.11 |

### 케이스 기록 템플릿

```markdown
#### CASE-{stock_code}-v{N}

- **종목**: {한글명} ({stock_code})
- **발견 일시**: {YYYY.MM.DD}
- **Fail Codes**: {F1_FINANCIAL_DRIFT, F2_VOLATILITY, ...}
- **드리프트 규모** (정량, 수치 없이 비율만):
  - 매출 {X}%
  - 주가 {Y}%
- **적용 대응**:
  - [ ] Re-rating v2 모드 전환
  - [ ] v1 섹션 보존 (반증 가능성)
  - [ ] Bear 확률 상향
  - [ ] Kill Condition 재정의
- **교훈** (1문장):
  > ...
```

---

## Appendix B. CHANGELOG

| Version | Date | 주요 변경 |
|---|---|---|
| **v15.0** | 2026.04.11 | **전면 재설계**: 상수 레지스트리, 모듈 아키텍처, 사례 부록화, 중복 제거 (5,268줄 → ~1,800줄) |
| v14.2 | 2026.04.11 | Pre-flight Checklist 초안 (현대건설 교훈 반영) — v15에 흡수 |
| v14.1 | 2026.04.04 | Evaluator v2 ALL PASS 시스템, HD건설기계 표준 CSS, SVG 15종 인라인 |
| v13.2 | 2026.04.03 | Jeff Sun 기술적 분석 지표 5종, 3-Stop 전략, KIS Backtest MCP 통합 |
| v13.1 | 2026.04.03 | Draw.io MCP, QuantAgent, 정량 분석 도구 체인 |
| v13 | 2026.04.03 | 15편 역설계, svg_radar 완전 금지, 산출물 3종 확정 (HTML+Excel+MD) |
| v12 | 2026.03.30 | SMIC 문체 완전 정립 (동사/본서는/전술한) |
| v11 | 2026.03.28 | 워크플로우 재설계 (엑셀 Single Source of Truth) |
| v10 | 2026.03.27 | KSS해운 실전 빌드 교훈 (서브에이전트 병렬, SVG 품질, 이미지 허용) |
| v9 | 2026.03.25 | YIG/SMIC/STAR/EIA 14건 벤치마크 종합, Key Debates, Variant Perception |
| v8 | 2026.03.20 | 89점+ 자동 달성 아키텍처 (Markdown-first) |
| v7 | 2026.03.18 | 스크롤 UX 5종 (진행률, Float TOC, 도트, Back to Top, 구분선) |

**상세 변경 이력**: `SKILL_legacy_v14_2_backup.md`의 해당 섹션 참조.

---

## Appendix C. 금지 규칙 모음 (NEVER-DO)

### 데이터
- ❌ Mock / 더미 / 추정 수치로 보고서 생성
- ❌ Phase 0 Pre-flight 미실행
- ❌ 원본 응답 미보존 (data/raw/ 없음)
- ❌ DART/MCP 실데이터 없이 빌더 하드코딩으로 시작

### 빌더/코드
- ❌ 종목별 수치를 SKILL.md에 하드코딩
- ❌ 임계값을 함수 내부에 inline (상수 레지스트리 사용)
- ❌ `smic_inject` 치환 규칙에 단독 숫자 (`'45,000'`) 추가 — 보호 영역 필요
- ❌ `sidebar_wrap` 안에 차트 삽입
- ❌ `add_source` + `chart_with_context` 동시 사용 (중복 차트 발생)

### 시각화
- ❌ `svg_radar()` 사용 (v13 이후 완전 금지)
- ❌ 3D 차트, 파이 6+ 슬라이스, 이중축 라인-라인
- ❌ 막대 Y축 0 미시작 (절단)
- ❌ 추정(E)과 실적(A) 색상 동일
- ❌ 하드코딩 색상 `#7c6af7` (CSS 변수 `var(--purple)` 사용)
- ❌ `border-radius: 8px` (4px 통일)

### 서술
- ❌ "약 N%", "대략", "정도로 추정", "보통", "통상적으로" (할루시네이션 패턴)
- ❌ "~할 것으로 기대된다", "~인 것으로 사료된다" (약한 종결)
- ❌ 기업명 직접 사용 (Cover 첫 등장 제외, 항상 "동사")
- ❌ 출처 없는 주장
- ❌ 정성 평가 ("좋다/나쁘다") — 숫자로 근거

### 밸류에이션
- ❌ 단일 방법론만 사용 (최소 2개 + Reverse DCF)
- ❌ Implied PER > 40x 무시 (Red Flag)
- ❌ 시나리오 확률 임의 할당 (역사적 분포 기반)
- ❌ "Why X? Why not Y?" 블록 누락

### 시스템
- ❌ MCP curl 호출에 `Accept: text/event-stream` 헤더 누락
- ❌ 치환 규칙을 Re-rating v2 블록에 무보호 적용
- ❌ v1 분석 섹션 완전 삭제 (반증 가능성 훼손)

---

## 부록: 빠른 참조 (Quick Reference)

### 신규 보고서 작성 순서

1. `config/{stock_code}.py` 작성 (종목 데이터만)
2. `preflight_validate(config, NexusMCPClient())` 실행 → Fail 시 대응 매트릭스
3. Phase 1~5 진행 (엑셀·본문·재검증)
4. `build(config)` → HTML 생성
5. `evaluate(html, SECTION_MINIMA)` → ALL PASS 확인
6. (조건부) Phase 6.5 백테스트
7. 사용자 검수 → 배포

### 자주 쓰는 상수 레퍼런스

- 재무 드리프트 한계: `PREFLIGHT.FINANCIAL_DRIFT_MAX` (기본 0.10)
- Re-rating 트리거: `PREFLIGHT.VOLATILITY_RERATING_TRIGGER` (기본 0.30)
- 최소 본문: `EVAL.TEXT_MIN` (기본 80,000)
- 동사 최소 빈도: `EVAL.DONGSA_MIN` (기본 40)
- 섹션별 최소: `SECTION_MINIMA["industry"].chars` (기본 10,000)
- 브랜드 색상: `CSS_VARS["purple"]` (`#7c6af7`)

### 모듈 의존성 한눈에

```
config → preflight → builder → post_processing → evaluator
                          ↓
                       sections
```

---

**본 SKILL.md v15.0은 모든 종목에 재사용 가능한 표준 프로토콜이다. 종목별 수치는 `config.py`에, 모든 임계값은 `preflight/thresholds.py`·`evaluator/criteria.py`에 있다. 이 문서에는 종목 하드코딩이 없다.**

**이전 버전 전체는 `SKILL_legacy_v14_2_backup.md` 참조.**
