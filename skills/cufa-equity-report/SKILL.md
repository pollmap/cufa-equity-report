---
name: cufa-equity-report
description: CUFA Equity Report v16 — 1인 AI 퀀트 운용사 실행 도구. 7섹션 HF 구조(BLUF→Thesis→Business→Numbers→Risks→Trade→Appendix) + Trade Ticket YAML + Evaluator v3(12개 binary) + Phase 7 피드백 루프. Nexus Finance MCP(398도구) → CUFA 보고서 → open-trading-api/QuantPipeline 선순환 파이프라인.
version: 16.0
last_updated: 2026-04-12
status: active
---

# CUFA Equity Report — SKILL v16.0

> **v16 설계 원칙** — 학회 분량 페티시 완전 폐기, HF/퀀트 실행가능성 중심 전환
> 1. **실행가능성 우선** — 보고서는 Trade Ticket으로 끝난다. HTML은 매개체일 뿐.
> 2. **12 binary 체크** — 분량·문체 카운팅 없음. "이걸 빼면 투자판단 지장?" 질문만.
> 3. **7섹션 HF 구조** — 11섹션 SMIC 구조 폐기. BLUF→Thesis→Business→Numbers→Risks→Trade→Appendix.
> 4. **피드백 루프** — Phase 7 분기별 복기로 실제 수익률 vs 추정치 추적.
> 5. **파이프라인 연동** — Nexus MCP → CUFA 보고서 → open-trading-api/QuantPipeline 선순환.

**이전 버전 백업**: `SKILL_legacy_v15_backup.md` / `SKILL_legacy_v14_2_backup.md`

---

## 목차

| # | 섹션 | 역할 |
|---|---|---|
| 0 | 철학 & 원칙 | 투자분석의 본질, 할루시네이션 방지, 1인 퀀트 운용사 정체성 |
| 1 | 표준 상수 레지스트리 | PreflightThresholds, Evaluator v3 Criteria, Trade Ticket Schema |
| 2 | 모듈 아키텍처 | 디렉토리 구조, 의존성 방향, trade_ticket/ 신규 모듈 |
| 3 | 워크플로우 Phase 0~7 | Pre-flight → Build → Evaluate → Trade Ticket → Backtest → 복기 |
| 4 | 7섹션 HF 구조 | BLUF/Thesis/Business/Numbers/Risks/Trade/Appendix 표준 |
| 5 | 시각화 표준 | SVG 10종, 금지 패턴, 차트 배치 |
| 6 | 밸류에이션 표준 | 방법론 8종, WACC, DCF, Football Field |
| 7 | Trade Implementation | Trade Ticket YAML, 진입/손절/목표, Kill Conditions |
| 8 | Evaluator v3 | 12개 binary 실행가능성 체크 |
| 9 | Cross-Skill 연동 & 피드백 루프 | quant-fund / QuantPipeline / Phase 7 복기 |
| 10 | Nexus MCP 통합 | 398도구 레지스트리, 데이터 수집 우선순위 |
| 11 | 산출물 | HTML + Excel 6시트 + Trade Ticket YAML + MD |
| App.A | 검증 케이스 아카이브 | 종목별 발견 사항 (하드코딩 금지) |
| App.B | CHANGELOG | v10→v16 변경 이력 |
| App.C | 금지 규칙 | NEVER-DO 리스트 |

---

## 0. 철학 & 원칙

### 0.1. 투자분석의 본질 — 확률적 추론 프레임워크

투자분석 보고서의 목적은 **주가를 맞히는 것이 아니다.** 확률을 높이는 과학적·정량적 연구 방법이다.

- 맞히더라도 벌지 못할 수 있고, 틀리더라도 벌 수 있다.
- **반증 가능성**: 모든 가정은 검증 가능해야 하고, 틀렸을 때 어디서 틀렸는지 추적 가능해야 한다.
- 성공하면 성공의 원인을, 실패하면 실패의 원인을 정량적으로 복기한다 (→ Phase 7).

**모든 주장은 5요건 충족:**
1. 정량적 근거 (뇌피셜 금지)
2. 근거의 출처 (추적 가능성)
3. 반증 조건 (어떤 수치가 나오면 틀린 건지)
4. 확률 표현 (Bull 20~25% / Base 50% / Bear 25~30%)
5. 사후 복기 가능 (Trade Ticket YAML + data/backtest/ 저장)

### 0.2. 할루시네이션 방지 — 결정론적 숫자 원칙

**LLM은 숫자를 "그럴듯하게" 만든다. 투자분석에서 가장 위험하다.**

| 숫자 유형 | 반드시 따라야 할 방식 | 금지 |
|---|---|---|
| 과거 실적 | DART/FnGuide 확정값 | AI가 기억에서 꺼내기 |
| 주가/시총 | pykrx/KRX 당일 종가 | "대략 X만원" |
| 베타(β) | KRX/Bloomberg 60M 주간 회귀 | "보통 1.0~1.5" |
| 무위험이자율(Rf) | 국고채 3년물 (ECOS 당일) | "3.5% 정도" |
| ERP | Damodaran 한국 ERP (연간) | "6% 적용" |
| 매출 추정 | P×Q 분해 → 각 변수 근거 명시 | "15% 성장 예상" |
| Target Multiple | Peer 평균/중앙값 + 프리미엄/할인 근거 | "PER 15배 적용" |

AI는 **계산기**처럼 작동해야 한다. 입력값이 확정되면 출력값은 결정론적이어야 한다.

### 0.3. Luxon AI 1인 퀀트 운용사 정체성

CUFA 보고서 v16은 **학회 발표용 문서가 아니라** Luxon AI 1인 헤지펀드의 리서치 산출물이다.

- **보고서 = 실행 도구**: 읽히고 끝나는 PDF가 아니라, Trade Ticket YAML → QuantPipeline 백테스트 → 분기별 복기로 이어지는 파이프라인의 시작점.
- **퀀트 실행가능성 우선**: "아름다운 보고서"보다 "이 포지션 내일 당장 들어갈 수 있는가?"
- **Nexus MCP 398도구 필수**: 데이터는 항상 MCP 먼저. 웹 스크래핑은 fallback.

### 0.4. 판단 기준 — 통합 테스트

모든 글자, 차트, 테이블은 **하나의 질문**으로 판단:
> "이걸 빼면 독자가 투자 판단을 내리는 데 지장이 있는가?"
> YES → 남긴다. NO → 삭제한다.

**금지**: 분량을 위한 분량, 메시지 없는 예쁜 차트, 뻔한 연혁/ESG 일반론.

---

## 1. 표준 상수 레지스트리

### 1.1. Pre-flight Thresholds (`preflight/thresholds.py`)

```python
@dataclass(frozen=True)
class PreflightThresholds:
    FINANCIAL_DRIFT_MAX: float = 0.10       # 빌더 vs 실데이터 괴리 한계
    OP_INCOME_SIGN_CHECK: bool = True       # 영업손익 부호 반전 시 STOP
    PRICE_DRIFT_MAX: float = 0.10           # 현재가 vs 빌더 괴리 한계
    VOLATILITY_RERATING_TRIGGER: float = 0.30  # 1년 수익률 절대값 초과 → Re-rating
    SELF_CONSISTENCY_TOLERANCE: float = 0.01   # PBR × BPS = Price 정합성
    MIN_YEARS_ACTUAL: int = 3               # 최소 실적 연도
    MIN_DAYS_OHLCV: int = 200               # 최소 주가 거래일 수
    REQUIRE_RAW_ARCHIVE: bool = True        # data/raw/ 원본 보존 필수

PREFLIGHT = PreflightThresholds()
```

### 1.2. Evaluator v3 Criteria (`evaluator/criteria.py`)

v2의 분량·문체 기반 → **12개 실행가능성 binary 체크**로 전환.

```python
@dataclass(frozen=True)
class EvaluatorV3Criteria:
    REQUIRE_OPINION: bool = True            # BUY/HOLD/SELL/WATCH/AVOID 명시
    REQUIRE_TARGET_PRICE: bool = True       # 숫자 목표주가
    REQUIRE_STOP_LOSS: bool = True          # 명시적 손절가 ← v16 NEW
    REQUIRE_POSITION_SIZE: bool = True      # position_size_pct (%) ← v16 NEW
    REQUIRE_BEAR_FLOOR: bool = True         # Bear Case 최소 하방
    REQUIRE_KILL_CONDITIONS_MIN: int = 3    # 투자 논리 무효화 조건 최소 3개
    REQUIRE_CATALYST_TIMELINE_MIN: int = 3  # 날짜 붙은 Catalyst 최소 3건
    REQUIRE_TRADE_TICKET: bool = True       # Trade Ticket 블록 파싱 가능 ← v16 NEW
    REQUIRE_DATA_SOURCES: bool = True       # 데이터 출처 1건 이상
    REQUIRE_BACKTEST_HOOK: bool = True      # QuantPipeline 연동 ← v16 NEW
    REQUIRE_FALSIFIABLE_THESIS: bool = True # 반증 조건 최소 1건
    REQUIRE_RISK_REWARD: bool = True        # Risk/Reward 수치 명시
    # HALLUCINATION_PATTERNS: PASS/FAIL 아님 — 경고만

EVAL_V3 = EvaluatorV3Criteria()
EVAL = EVAL_V3  # 하위 호환
```

### 1.3. Trade Ticket Schema (`trade_ticket/schema.py`)

```python
class TradeOpinion(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    WATCH = "WATCH"   # 진입 조건 미달 — 모니터링
    AVOID = "AVOID"   # 명시적 회피

@dataclass
class TradeTicket:
    ticker: str                     # "329180.KS"
    company_name: str
    opinion: TradeOpinion
    entry_price: float
    stop_loss: float                # 손절가 — 필수
    target_price: float
    horizon_months: int             # 투자 기간
    position_size_pct: float        # 포트폴리오 내 비중 (%)
    risk_reward: float              # (TP - Entry) / (Entry - SL)
    kill_conditions: tuple[str, ...]  # 최소 3개
    catalyst_timeline: tuple[CatalystEvent, ...]  # 최소 3건
    scenario: ScenarioBand | None
    backtest_engine: str = "open-trading-api/QuantPipeline"
    report_version: str = "v16"
    generated_at: str = ""          # ISO date
```

### 1.4. Industry Checklist Registry (`preflight/industry_checklist.py`)

v16 추가: **조선** 11개 항목.

```python
INDUSTRY_CHECKLIST: dict[str, tuple[str, ...]] = {
    "조선": (
        "수주잔고 상세 (선종/발주처/금액/건조연도)",
        "Slot 가용 현황 (연도별 도크 배정 현황)",
        "건조단가 추이 (CBM/CGT 기준)",
        "강재 원가 비중 + 후판 가격 민감도",
        "LNG 운반선 발주 사이클 위치",
        "환율 민감도 (수출 90%+ → USD/KRW)",
        "외주/협력사 의존도 (숙련공 수급)",
        "기자재 국산화율 + 핵심 부품 조달",
        "인도 스케줄 + 지연 리스크",
        "해양플랜트 잔존 리스크 (클레임/손충)",
        "글로벌 경쟁사 수주 점유율 (현대/삼성/中 비교)",
    ),
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

### 1.5. 임계값 변경 정책

기본 상수 **수정 금지**. 종목별 특이치가 필요하면 상속 후 오버라이드:
```python
@dataclass(frozen=True)
class BioPreflightThresholds(PreflightThresholds):
    MIN_YEARS_ACTUAL: int = 2  # 바이오 신생기업: 3년 실적 없을 수 있음
```

---

## 2. 모듈 아키텍처

### 2.1. 디렉토리 구조 (v16 표준)

```
cufa-equity-report/
├── SKILL.md                      ← 본 문서
├── SKILL_legacy_v15_backup.md    ← v15 백업
├── SKILL_legacy_v14_2_backup.md  ← v14 백업
├── CHANGELOG.md
│
├── preflight/                    ← Phase 0 검증
│   ├── thresholds.py             ← PreflightThresholds
│   ├── checker.py                ← preflight_validate()
│   ├── mcp_client.py             ← NexusMCPClient
│   ├── dart_parser.py            ← CFS/OFS 분리 파서
│   ├── tool_schemas.py           ← MCP 도구 인자 레지스트리
│   └── industry_checklist.py     ← INDUSTRY_CHECKLIST (조선 포함 9종)
│
├── config/                       ← 종목별 설정
│   ├── _template.py              ← StockConfig (v16: trade_ticket/kill_conditions 추가)
│   └── {stock_code}.py           ← 실제 종목 config
│
├── builder/                      ← HTML 빌드 엔진
│   ├── core.py                   ← build_report() 오케스트레이터
│   ├── helpers.py                ← section_header, sidebar_wrap, table
│   ├── svg.py                    ← SVG 헬퍼 10종
│   ├── components.py             ← counter_arg, callout, expand_card
│   ├── design_tokens.py          ← CSS_VARS, CHART_COLOR_ROLES
│   └── css.py                    ← gen_css() (ticket-box/thesis-box 포함)
│
├── trade_ticket/                 ← v16 신규 모듈 ⭐
│   ├── __init__.py
│   ├── schema.py                 ← TradeTicket 스키마 + validate_trade_ticket()
│   ├── generator.py              ← config → TradeTicket 생성
│   ├── backtest_hook.py          ← QuantPipeline 연동
│   └── feedback.py               ← Phase 7 복기 엔진
│
├── evaluator/                    ← v3 자동 검증
│   ├── criteria.py               ← EvaluatorV3Criteria (12 binary)
│   └── run.py                    ← evaluate() 통합 실행
│
├── post_processing/
│   ├── protect_replace.py        ← 보호-치환-복원 패턴
│   └── rerating_note.py          ← Re-rating v2 블록 생성
│
├── sections/                     ← 7섹션 HF 빌더
│   ├── base.py                   ← SectionData + assemble_section()
│   ├── section1_bluf.py          ← Investment Summary
│   ├── section2_thesis.py        ← 3축 Thesis
│   ├── section3_business_setup.py
│   ├── section4_numbers.py
│   ├── section5_risks.py
│   ├── section6_trade.py         ← Trade Implementation ⭐
│   └── section7_appendix.py
│
└── output/                       ← 생성 결과
    ├── {종목명}_CUFA_보고서.html
    ├── {종목명}_trade_ticket.yaml  ← v16 신규
    ├── {종목명}_재무데이터.xlsx
    └── data/
        ├── raw/                  ← MCP 원본 응답
        ├── backtest/             ← QuantPipeline 결과
        └── feedback/             ← Phase 7 복기 리포트
```

### 2.2. 의존성 방향

```
config → preflight → builder → post_processing → evaluator → output
                          ↓                                       ↑
                       sections                       trade_ticket/
```

하위 모듈은 상위 모듈을 import하지 못한다.

### 2.3. v16 StockConfig 핵심 필드

```python
@dataclass(frozen=True)
class StockConfig:
    # ... 기존 필드 유지 ...

    # v16 신규 필드
    trade_ticket: dict = field(default_factory=dict)
    # {"opinion": "BUY", "stop_loss": 410000, "position_size_pct": 5.0,
    #  "entry_price": 475000, "horizon_months": 12}

    kill_conditions: tuple[str, ...] = ()
    # ("수주잔고 YoY -20% 이하", "강재 원가 +40% 이상", "핵심 경쟁사 슬롯 잠식")

    backtest_config: dict = field(default_factory=dict)
    # {"engine": "open-trading-api/QuantPipeline", "benchmark": "KOSPI",
    #  "slippage_bps": 10}

    feedback_loop: dict = field(default_factory=dict)
    # {"enabled": True, "review_cycle_months": 3, "output_dir": "data/feedback"}
```

---

## 3. 워크플로우 Phase 0~7

### 3.1. 표준 파이프라인

```
Phase 0: Pre-flight 검증           [MCP 실호출, 10~15분]
   ↓
Phase 1: 리서치 + config.py 작성   [30~60분]
   ↓
Phase 2: 엑셀 v1 빌드              [데이터 → xlsx 6시트, 15분]
   ↓
Phase 3: 투자포인트 3개 + Kill 3개 초안  [사용자 승인 게이트]
   ↓
Phase 4: 7섹션 본문 작성           [60~120분, 서브에이전트 가능]
   ↓
Phase 5: 엑셀 v2 최종 업데이트     [본문 수치 → xlsx 역반영]
   ↓
Phase 6: HTML 빌드 + Evaluator v3  [12/12 ALL PASS 루프]
   + Trade Ticket YAML 생성
   ↓
Phase 6.5: Backtest 실행 (선택)    [QuantPipeline 백테스트]
   ↓
Phase 7: 투자 실행 복기 (장기)     [분기별 actual vs estimated]
```

**Re-rating 분기**: Phase 0의 `F2_VOLATILITY`(±30%) 또는 `F1_SIGN_FLIP`(영업손익 부호 반전) → Re-rating v2 모드.

### 3.2. Phase 0 — Pre-flight 5점 체크

```
□ ① 재무제표 실시간 검증 [CRITICAL]
   MCP dart_financial_statements 실호출
   Check: |builder - actual| / actual > 0.10 → F1_FINANCIAL_DRIFT
   Check: sign(builder_op) ≠ sign(actual_op) → F1_SIGN_FLIP

□ ② 주가 실시간 검증 [CRITICAL]
   MCP stocks_history 실호출
   Check: |builder_price - actual| / actual > 0.10 → F2_PRICE_DRIFT
   Flag: |1년 수익률| > 0.30 → F2_VOLATILITY

□ ③ 삼각검증 (PBR·BPS·Price) [CRITICAL]
   Check: PBR × BPS ≠ Price (오차 > 1%) → F3_TRIPLE_CHECK

□ ④ 원본 응답 파일 보존 [MANDATORY]
   Save: data/raw/{stock_code}_{tool}_{YYYYMMDD}.raw

□ ⑤ 산업 체크리스트 로드
   INDUSTRY_CHECKLIST[config.industry] 전 항목 확인
```

### 3.3. Pre-flight 실패 대응

| Fail Code | 표준 대응 |
|---|---|
| `F1_FINANCIAL_DRIFT` | MCP 실데이터 교체, config 재작성, 본문 논지 재검토 |
| `F1_SIGN_FLIP` | Kitchen Sinking vs 실적 악화 판정 (§3.4) |
| `F2_PRICE_DRIFT` | 현재가 갱신 + 상대지표(Upside/R-R) 재계산 |
| `F2_VOLATILITY` | **Re-rating v2 모드** 전환 |
| `F3_TRIPLE_CHECK` | config 수치 재검증 |
| `F4_RAW_MISSING` | 즉시 재호출 + 저장 |
| `F5_INDUSTRY` | INDUSTRY_CHECKLIST 2차 MCP 호출 |

### 3.4. Kitchen Sinking 판정 프레임

| 검증 항목 | Kitchen Sinking 신호 | 실적 악화 신호 |
|---|---|---|
| OCF/NI Ratio | > 1.0 (OCF 건전) | < 0.5 |
| Accruals Ratio | 음수 | 양수 |
| 전년 대비 매출 | 성장 지속 | 감소 |
| 충당금 성격 | 일회성 분류 공시 | 기조적 비용 증가 |
| 익년 가이던스 | 정상화 제시 | 악화 지속 |

### 3.5. Phase 7 — 분기별 복기

```python
# trade_ticket/feedback.py
result = run_feedback_loop(
    ticket=my_ticket,
    result=backtest_result,
    analyst_notes="2025Q4 LNG 발주 확인됨",
    assumption_deltas=[
        AssumptionDelta("revenue_growth", 0.15, 0.08, "중국 덤핑"),
    ],
    output_dir=Path("data/feedback"),
)
# output: data/feedback/{ticker}_feedback_{date}.md
```

---

## 4. 7섹션 HF 구조

v15의 11섹션 SMIC 구조 → **7섹션 HF(헤지펀드) 구조**로 전환.

| # | 섹션 ID | 제목 | 핵심 구성 |
|---|---|---|---|
| 1 | `s1_bluf` | Investment Summary | 투자의견/TP/SL/R-R, 3축 Thesis 1줄, Bear Floor, Catalyst Timeline |
| 2 | `s2_thesis` | 투자 Thesis | 3축 통합 논리 (각 축: 논거 + 반증 조건 + 수익 임팩트) |
| 3 | `s3_business` | Business & Industry Setup | 사업구조, 산업 포지셔닝, 경쟁 해자, 산업 체크리스트 |
| 4 | `s4_numbers` | The Numbers | 재무분석 + Peer 비교 + 실적추정 + 밸류에이션 통합 |
| 5 | `s5_risks` | Risks — Bear Case First | Bear Case 먼저, Kill Conditions 3+개, EPS 민감도 |
| 6 | `s6_trade` | Trade Implementation | Trade Ticket, 진입/손절/목표, 포지션 비중, QuantPipeline |
| 7 | `s7_appendix` | Appendix | A-1 재무3표, A-2 Peer, A-3 DCF 가정, A-4 출처·방법론 |

### 4.1. §1 BLUF — Investment Summary

**핵심 원칙**: 이 섹션만 읽어도 투자 판단 가능. 1페이지 이내.

필수 구성요소:
- 5-cell Metric Grid: 투자의견 / TP / 현재가 / SL / R-R
- `.thesis-box`: 3축 Thesis 1줄 요약
- Bear Case callout (하방 가격 + %)
- Catalyst Timeline table (3건+)

```python
# sections/section1_bluf.py
from sections import build_section1
html = build_section1(config)
```

### 4.2. §6 Trade Implementation — 보고서의 정점

**이 섹션이 v16의 핵심**. 읽고 끝나는 분석이 아니라 실행 도구.

필수 구성요소:
- `.ticket-box`: Trade Ticket 요약 (opinion/entry/SL/TP/size/horizon)
- `.ticket-yaml`: YAML 코드블록 (QuantPipeline이 직접 파싱)
- Kill Conditions `<ul>` (최소 3개)
- Backtest 연동 주석 (`backtest_engine: open-trading-api/QuantPipeline`)

### 4.3. §5 Risks — Bear Case First 원칙

v15는 리스크를 마지막에 배치 → **v16는 Bull Case보다 Bear Case 먼저**.
"최악이 얼마나 나쁜가?"를 먼저 정량화하고 그 다음 Bull을 검토한다.

---

## 5. 시각화 표준

### 5.1. 허용 SVG 10종

| 함수 | 용도 |
|---|---|
| `svg_bar()` | 연도별 매출/이익 막대 |
| `svg_line()` | 주가/추이 라인 |
| `svg_scatter()` | OPM-PER / ROE-PBR 산점도 |
| `svg_heatmap()` | 민감도 히트맵 |
| `svg_waterfall()` | 영업이익 브리지 |
| `svg_donut()` | 사업부 매출 비중 |
| `svg_football()` | Football Field 밸류에이션 |
| `svg_dual_axis()` | 매출+OPM 이중 축 |
| `svg_stacked_bar()` | 분기별 누적 막대 |
| `svg_area()` | 잉여현금흐름 면적 |

### 5.2. 차트 배치 규칙

- 섹션 **마지막**에 배치 (본문 텍스트 먼저)
- 2개씩 `.chart-pair` 그리드 배치
- 각 차트에 **메시지 한 줄** 타이틀 필수 ("매출 성장 가속, OPM 회복")
- `.chart-box` 배경: 반드시 `#ffffff` (다크 배경에서 SVG 대비 확보)

### 5.3. 금지 패턴

- **레이더/스파이더 차트 절대 금지** (`svg_radar` 삭제됨)
- 빈 차트 / 하드코딩 목업 데이터 금지
- 메시지 없는 장식용 차트 금지
- `.sidebar-wrap` 안에 차트/테이블 삽입 금지 (텍스트만 허용)

---

## 6. 밸류에이션 표준

### 6.1. 방법론 8종 매트릭스

| 방법론 | 적용 조건 | 필수 입력 |
|---|---|---|
| PER | EPS > 0, 주기적 실적 | Fwd EPS, Peer PER 분포 |
| PBR | 자산 집약적 업종 | BPS, ROE 프리미엄/할인 근거 |
| EV/EBITDA | 부채 수준 차이 큰 Peer | EBITDA, Net Debt, Peer EV/EBITDA |
| DCF | 안정적 FCF 예측 가능 | WACC, 성장률, Terminal Value |
| SOTP | 복합 사업 구조 | 사업부별 독립 밸류에이션 |
| Reverse DCF | 현주가 implied 성장률 검증 | 현재 주가, WACC |
| Dividend DDM | 배당 정책 안정적 기업 | DPS, 배당 성장률 |
| 시가총액/수주잔고 | 조선·건설·방산 | 수주잔고, 업력 PBR |

**표기 기준 명시 필수**: PER/PBR/EV-EBITDA → Forward/Trailing/TTM/12MF 반드시 표기.

### 6.2. WACC 계산 표준

```
Rf = 국고채 3년물 (ECOS 당일)
β = KRX 60M 주간 회귀
ERP = Damodaran 한국 ERP (연간)
WACC = Rf + β × ERP + 추가 위험 프리미엄
```

### 6.3. Football Field 표준 (§4 Numbers 필수)

- PER / PBR / EV/EBITDA / DCF 최소 4개 방법론
- 각 방법론별 Min/Mid/Max 밸류 표시
- 현재가 수직선 표시
- SVG `svg_football()` 함수 사용

---

## 7. Trade Implementation Standard

### 7.1. Trade Ticket YAML — 기계 판독 가능 포맷

Trade Ticket은 보고서의 최종 산출물이다. QuantPipeline이 직접 파싱한다.

```yaml
# {종목명}_trade_ticket.yaml
ticker: 329180.KS
company_name: HD한국조선해양
opinion: BUY
entry_price: 475000
stop_loss: 410000          # 명시적 손절가 필수
target_price: 528750
horizon_months: 12
position_size_pct: 5.0     # 포트폴리오 비중 필수
risk_reward: 1.42          # (TP - Entry) / (Entry - SL)
kill_conditions:
  - "수주잔고 YoY -20% 이하로 붕괴"
  - "강재 원가 YoY +40% 이상 + OPM 역전"
  - "핵심 경쟁사 슬롯 잠식 (점유율 -10%p)"
catalyst_timeline:
  - date: "2025Q3"
    event: "LNG 운반선 대규모 슬롯 계약 발표"
  - date: "2026Q1"
    event: "25년 연간 실적 확인 + 가이던스"
  - date: "2026Q2"
    event: "중동 FLNG 프로젝트 수주 발표"
backtest_engine: open-trading-api/QuantPipeline
report_version: v16
generated_at: "2026-04-12"
```

### 7.2. 생성 방법

```python
from trade_ticket import generate_trade_ticket, ticket_to_yaml, validate_trade_ticket

ticket = generate_trade_ticket(config)   # config.trade_ticket 필드 읽음
errors = validate_trade_ticket(ticket)   # 12개 필드 검증
if not errors:
    yaml_str = ticket_to_yaml(ticket)    # YAML 직렬화
    Path("output/{종목}_trade_ticket.yaml").write_text(yaml_str)
```

### 7.3. Kill Conditions 작성 기준

- 최소 3개, **정량적** 조건 (숫자 포함)
- "이 조건이 충족되면 즉시 포지션 청산" 수준의 구체성
- 투자 Thesis의 각 축마다 1개 이상 대응

**좋은 예**: "수주잔고 YoY -20% 이하로 붕괴"
**나쁜 예**: "업황이 나빠지면" (비정량, 비가동)

### 7.4. Position Sizing 기준

| R/R | 컨빅션 | 포지션 비중 |
|---|---|---|
| ≥ 3.0x | 매우 높음 | 7~10% |
| 2.0~2.9x | 높음 | 4~6% |
| 1.5~1.9x | 보통 | 2~3% |
| < 1.5x | 낮음 | WATCH/AVOID |

---

## 8. Evaluator v3

### 8.1. 12개 binary 체크

```python
from evaluator.run import evaluate
result = evaluate(html_string)
print(result.format_report())
# === Evaluator v3 — 12 / 12 PASS === ✅ ALL PASS
```

| # | 체크 키 | 탐지 패턴 | 실패 시 |
|---|---|---|---|
| 1 | `opinion` | BUY/HOLD/SELL/매수/매도 | 투자의견 추가 |
| 2 | `target_price` | TP/목표주가 + 숫자 | 목표주가 명시 |
| 3 | `stop_loss` | 손절가/stop_loss + 숫자 | SL 명시 |
| 4 | `position_size` | position_size_pct/비중 % | 비중 추가 |
| 5 | `bear_floor` | Bear/하방/최악 | Bear Case 추가 |
| 6 | `kill_conditions` | kill.condition/Kill × 3+ | Kill Condition 추가 |
| 7 | `catalyst_timeline` | 날짜 + Catalyst × 3+ | 날짜 붙은 이벤트 추가 |
| 8 | `trade_ticket` | trade.ticket/ticket-box | §6 Trade 섹션 점검 |
| 9 | `data_sources` | DART/KRX/ECOS/출처 | 데이터 출처 명시 |
| 10 | `backtest_hook` | backtest/QuantPipeline | §6에 backtest_engine 추가 |
| 11 | `falsifiable_thesis` | 틀리면/무효화/Kill Condition | 반증 조건 추가 |
| 12 | `risk_reward` | R/R/risk_reward + 숫자 | R-R 수치 추가 |

### 8.2. ALL PASS 루프

```python
# Phase 6 표준 루프
while True:
    ctx = build_report(config, [build_section1, ..., build_section7])
    result = evaluate(ctx.output_html)
    if result.all_passed:
        write_output(ctx, config)
        break
    # FAIL 항목 자동 수정 후 재빌드
    for key in result.failing_keys():
        fix_section(key, config)
```

---

## 9. Cross-Skill 연동 & 피드백 루프

### 9.1. 파이프라인 아키텍처

```
Nexus Finance MCP (398도구)
  ↓ 데이터 수집 (Phase 0~1)
CUFA Report v16
  ├─ OUTPUT: Trade Ticket YAML
  │    └─ open-trading-api/QuantPipeline (백테스트)
  │         └─ backtest_result.json → Phase 7 feedback.py
  │              └─ 파라미터 조정 → 다음 보고서 개선
  ├─ OUTPUT: 거시지표 태그 → macro-dashboard 스킬
  ├─ OUTPUT: 공모전 포맷 → competition-arsenal 스킬
  └─ INPUT: 이전 보고서 피드백 ← Phase 7 FeedbackReport
```

### 9.2. QuantPipeline 연동

```python
from trade_ticket.backtest_hook import submit_to_backtest

result = submit_to_backtest(
    ticket=ticket,
    output_dir=Path("data/backtest"),
)
# OPEN_TRADING_API_PATH env 또는 ~/Desktop/open-trading-api 자동 탐색
# 결과: data/backtest/{ticker}_backtest_{date}.json
```

### 9.3. Phase 7 피드백 루프

분기별 복기 3단계:

```
1. 실제 수익률 vs 추정 수익률 비교
2. kill_conditions 발동 여부 확인
3. 가정 편차(AssumptionDelta) 분석 → SKILL 파라미터 조정
```

편차 분류:
- **Excellent**: ±5% 이내 → 가정 유지
- **Acceptable**: ±15% → 모니터링
- **Review**: ±30% → 가정 재검토
- **Major Miss**: >30% → 투자 논리 전면 재검토

---

## 10. Nexus MCP 통합

### 10.1. 데이터 수집 우선순위 (절대 규칙)

1. **Nexus MCP 398도구 먼저** — 건너뛰기 금지
2. **직접 API** (DART, KRX, KIS) — MCP에 없는 데이터만
3. **웹 스크래핑** — 1, 2 모두 불가할 때만 fallback

### 10.2. Phase 0~1 핵심 MCP 도구

| 데이터 | MCP 도구 | 비고 |
|---|---|---|
| 재무제표 (CFS) | `dart_financial_statements` | 연결 전용 |
| 주가 이력 | `stocks_history` | start=today-365 |
| 컨센서스 | `consensus_estimates` | Fwd EPS/매출 |
| Peer 데이터 | `peer_comparison` | OPM/PER/PBR |
| 수주잔고 (조선/건설) | `dart_disclosures` | 공시 파싱 |
| ECOS 금리 | `ecos_get_statistic` | 국고채 3년물 |
| Damodaran ERP | `damodaran_erp` | 한국 ERP |

### 10.3. CFS 전용 원칙

재무제표는 **반드시 연결(CFS)** 사용. 별도(OFS) 절대 금지.
`dart_parser.split_cfs_ofs()` 로 분리 후 CFS만 사용.

---

## 11. 산출물 & Excel 6시트

### 11.1. 최종 산출물 3종

| 파일 | 내용 | 용도 |
|---|---|---|
| `{종목}_CUFA_보고서.html` | 7섹션 인터랙티브 HTML | 웹 열람, 공유 |
| `{종목}_trade_ticket.yaml` | Trade Ticket YAML | QuantPipeline 파싱 |
| `{종목}_재무데이터.xlsx` | Excel 6시트 | 모델링, 백테스트 |

v15 Excel 16시트 → **v16 Excel 6시트** (핵심만 유지):

| 시트 | 내용 |
|---|---|
| `IS` | 손익계산서 5년 |
| `BS` | 재무상태표 5년 |
| `CF` | 현금흐름표 5년 |
| `Estimates` | 실적추정 + P×Q 분해 |
| `Valuation` | DCF + Football + Peer |
| `TradeTicket` | Trade Ticket 파라미터 |

### 11.2. HTML 구조 표준

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <style>{gen_css()}</style>  <!-- ticket-box/thesis-box 포함 -->
</head>
<body>
  <div class="sticky-header">...</div>
  <div class="report">
    <!-- §1~§7 section 블록 -->
    <div id="reading-progress"></div>
    <div class="ai-watermark">AI-Assisted Research — CUFA × Nexus MCP</div>
  </div>
</body>
```

---

## Appendix A — 검증 케이스 아카이브

케이스 형식: `CASE-{stock_code}-v{N}` — 종목별 발견 사항만 기록. 하드코딩 금지.

### CASE-329180-v1 (HD한국조선해양, 2026-04-12)

- **HF 프로토타입 → 12/12 Evaluator v3 PASS** (v16 설계 검증 기준)
- Kill Condition 3개: 수주잔고/-20%/강재원가/슬롯점유율
- Trade Ticket R/R: 1.42x (Entry 475K / SL 410K / TP 528.75K)
- 조선 산업 체크리스트: LNG 발주 사이클, 강재 원가, 슬롯 가용성 검증 완료

---

## Appendix B — CHANGELOG

### v16.0 — 2026-04-12

**Breaking Changes:**
- Evaluator v2 (분량/문체 기반) → v3 (실행가능성 binary 12개)
- SMIC 문체 강제 (동사/본서/전술한) 완전 폐기
- 11섹션 → 7섹션 HF 구조
- `sections/minima.py` 삭제 (섹션별 최소 자수 폐기)
- `post_processing/smic_injector.py` 삭제
- `sections/section1_company.py` ~ `section11_appendix.py` 11개 삭제

**신규:**
- `trade_ticket/` 모듈 신설 (schema/generator/backtest_hook/feedback)
- `sections/section1_bluf.py` ~ `section7_appendix.py` 7개 신설
- Phase 7 피드백 루프 신설
- `StockConfig`에 trade_ticket/kill_conditions/backtest_config/feedback_loop 필드 추가
- CSS: `.ticket-box` / `.thesis-box` 클래스 추가
- 조선 산업 체크리스트 추가 (11개 항목)

---

## Appendix C — 금지 규칙 (NEVER-DO)

### 데이터
- AI 기억에서 숫자 꺼내기 (할루시네이션)
- CFS 대신 OFS 사용
- MCP 건너뛰고 웹 스크래핑 먼저
- PER/PBR/EV-EBITDA에 Forward/Trailing 기준 미표기

### 섹션 구성
- 분량을 위한 분량 (80K자 채우기 게임)
- 메시지 없는 장식용 차트
- 레이더/스파이더 차트 (`svg_radar` 삭제됨)
- `.sidebar-wrap` 안에 차트/테이블 삽입
- 투자포인트 없이 기업 소개만 나열

### Trade Ticket
- 손절가(SL) 없는 보고서
- Position Size 없는 보고서
- Kill Conditions < 3개
- Catalyst Timeline 날짜 미기재
- R/R 수치 미기재

### 평가
- Evaluator v3 ALL PASS 전 보고서 납품
- v2(분량/SMIC) 기준으로 평가

---

## Quick Reference — 체크리스트

### Phase 0 완료 기준
- [ ] 재무제표 MCP 호출 + `data/raw/` 저장
- [ ] 주가 1년 이력 MCP 호출
- [ ] PBR × BPS ≈ Price (1% 이내)
- [ ] 산업 체크리스트 전 항목 확인

### Phase 3 게이트
- [ ] 투자포인트 3개 초안 + 사용자 승인
- [ ] Kill Conditions 3개+ 초안
- [ ] Trade Ticket 파라미터 초안 (SL/size/R-R)

### Phase 6 완료 기준
- [ ] Evaluator v3 12/12 ALL PASS
- [ ] Trade Ticket YAML 파일 생성 + 검증
- [ ] Excel 6시트 완성
- [ ] HTML 브라우저 렌더링 확인

### Phase 7 트리거
- [ ] 분기별 실제 수익률 기록
- [ ] Kill Conditions 발동 여부 체크
- [ ] 주요 가정 편차 분석 + SKILL 업데이트
