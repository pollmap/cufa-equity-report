# CUFA Equity Report Skill v15.1

> 충북대학교 가치투자학회(CUFA) 공식 기업분석보고서 생성 표준 스킬.
> 모든 종목에 재사용 가능한 **모듈화된 프로토콜**.
> Phase 0 Pre-flight → Build → Evaluator v2 ALL PASS → Re-rating Note(조건부).

**핵심 원칙**: 모든 숫자에는 출처가 있고, 모든 가정에는 반증 조건이 있다.

---

## Quick Start

```python
from config._template import StockConfig
from preflight import preflight_validate, NexusMCPClient
from builder import build_report, write_output
from evaluator import evaluate
from post_processing import smic_inject
from sections import SectionData, SECTION_BUILDERS

# 1) 종목 config 작성 (config/000720.py)
config = StockConfig(
    stock_code="000720",
    company_name="현대건설",
    company_name_en="Hyundai E&C",
    market="KOSPI",
    industry="건설",
    subtitle="중동 르네상스와 국내 재건축의 교차점",
    builder_revenue=326_703 * 1e8,
    builder_op_income=-12_634 * 1e8,
    builder_price=179_500,
    builder_bps=86_548,
    builder_eps_next=11_635,
    shares_outstanding=111_723_419,
    target_year=2024,
)

# 2) Phase 0 — Pre-flight 검증
result = preflight_validate(config, NexusMCPClient())
if result.has_fail():
    if result.is_rerating_mode():
        # F2_VOLATILITY → Re-rating v2 모드 전환
        ...
    else:
        # F1/F3/F4/F5 → config 또는 데이터 교체
        raise SystemExit(result.fail_codes)

# 3) 섹션 데이터 작성 → 빌드
sections = []
for num, builder in SECTION_BUILDERS.items():
    data = SectionData(
        keywords=[...],
        narrative_html="...",
        charts=[...],
        tables=[...],
    )
    sections.append(lambda c, d=data, b=builder: b(c, d))

ctx = build_report(
    config, sections,
    opinion="BUY", target_price=200_000, current_price=179_500,
    post_process=lambda h: smic_inject(h, config.company_name),
)

# 4) 결과 저장 + Evaluator 검증
out_path = write_output(ctx, config)
eval_result = evaluate(ctx.output_html)
if not eval_result.all_passed:
    print("ALL PASS 실패:", eval_result.failed_checks())
```

---

## 모듈 아키텍처 (v15.1)

```
cufa-equity-report/
├── SKILL.md                      ← 규칙·프로토콜 (1,306줄)
├── README.md                     ← 본 문서
├── CHANGELOG.md                  ← 버전 이력
├── skill.meta.json               ← 메타데이터
│
├── preflight/                    ← Phase 0 검증 (7 files, 80K)
│   ├── thresholds.py             ← PREFLIGHT 상수
│   ├── checker.py                ← preflight_validate()
│   ├── mcp_client.py             ← NexusMCPClient (SSE)
│   ├── dart_parser.py            ← CFS/OFS 분리
│   ├── industry_checklist.py     ← INDUSTRY_CHECKLIST (8개)
│   └── tool_schemas.py           ← MCP 도구 스키마
│
├── config/                       ← 종목별 설정
│   ├── _template.py              ← StockConfig 템플릿
│   └── {stock_code}.py           ← 실제 종목
│
├── builder/                      ← HTML 빌드 엔진 (10 files, 290K)
│   ├── core.py                   ← build_report() 오케스트레이터
│   ├── css.py                    ← gen_css() 단일 표준
│   ├── design_tokens.py          ← CSS_VARS, 색상 역할
│   ├── figure.py                 ← FigureCounter 클래스
│   ├── svg.py                    ← 32종 SVG 차트
│   ├── helpers.py                ← section_header, sidebar_wrap, table
│   ├── components.py             ← counter_arg, expand_card 등 9종
│   ├── markdown.py               ← md_to_html()
│   └── phase65_backtest.py       ← Nexus backtest_run 래퍼
│
├── sections/                     ← 11섹션 스캐폴더 (14 files)
│   ├── base.py                   ← SectionData, assemble_section()
│   ├── minima.py                 ← SECTION_MINIMA (섹션별 최소치)
│   ├── section1_company.py       ← 기업개요
│   ├── section2_industry.py      ← 산업분석
│   ├── section3_ip1.py           ← 투자포인트 I
│   ├── section4_ip2.py           ← 투자포인트 II
│   ├── section5_ip3.py           ← 투자포인트 III
│   ├── section6_financial.py     ← 재무분석
│   ├── section7_peer.py          ← Peer 비교
│   ├── section8_estimate.py      ← 실적추정
│   ├── section9_valuation.py     ← 밸류에이션
│   ├── section10_risk.py         ← 리스크
│   └── section11_appendix.py     ← Appendix
│
├── evaluator/                    ← v2 자동 검증 (3 files, 9K)
│   ├── criteria.py               ← EvaluatorCriteria 상수
│   └── run.py                    ← evaluate() → EvaluationResult
│
└── post_processing/              ← 빌드 후 처리 (4 files, 10K)
    ├── protect_replace.py        ← 보호-치환-복원 패턴
    ├── smic_injector.py          ← '동사' 문체 주입
    └── rerating_note.py          ← Re-rating v2 블록 생성
```

### 모듈 의존성 (DAG)

```
config → preflight → builder → post_processing → evaluator → output
                         ↓
                     sections
```

---

## 표준 상수 (모든 종목 동일)

### PreflightThresholds

| 상수 | 값 | 의미 |
|---|---:|---|
| `FINANCIAL_DRIFT_MAX` | 0.10 | 재무 드리프트 한계 (10%) |
| `PRICE_DRIFT_MAX` | 0.10 | 주가 드리프트 한계 (10%) |
| `VOLATILITY_RERATING_TRIGGER` | 0.30 | Re-rating Mode 트리거 (±30%) |
| `SELF_CONSISTENCY_TOLERANCE` | 0.01 | PBR×BPS=Price 정합성 |
| `MIN_YEARS_ACTUAL` | 3 | 과거 실적 최소 연수 |
| `MIN_DAYS_OHLCV` | 200 | OHLCV 최소 거래일 |

### EvaluatorCriteria (v2 HARD_MIN)

| 체크 | 기준 | 비고 |
|---|---:|---|
| `TEXT_MIN` | 80,000자 | 본문 분량 |
| `SVG_MIN` | 25개 | 차트 최소 |
| `TABLE_MIN` | 25개 | 테이블 최소 |
| `H2H3_MIN` | 20개 | 소제목 최소 |
| `BOLD_FIRST_MIN` | 150개 | 볼드 첫문장 |
| `TRANSITIONS_MIN` | 30개 | 전환어 빈도 |
| `DONGSA_MIN` | 40회 | "동사" 호칭 |
| `COUNTER_ARG_MIN` | 3개 | 반박 블록 |
| `APPENDIX_MIN` | 16개 | 부록 최소 |
| `HALLUCINATION_PATTERNS` | 0건 | "약 N%", "대략" 등 |

---

## Fail Code 체계

| Code | 의미 | 대응 |
|---|---|---|
| `F1_FINANCIAL_DRIFT` | 재무 드리프트 > 10% | 실데이터 교체 |
| `F1_SIGN_FLIP` | 영업손익 부호 반전 | Kitchen Sinking 판정 |
| `F2_PRICE_DRIFT` | 주가 드리프트 > 10% | 현재가 갱신 |
| `F2_VOLATILITY` | 1년 수익률 > ±30% | **Re-rating v2 모드** |
| `F3_TRIPLE_CHECK` | PBR × BPS ≠ Price | config 재검증 |
| `F4_RAW_MISSING` | 원본 응답 미보존 | 재호출 + 저장 |
| `F5_INDUSTRY` | 산업 체크리스트 누락 | 2차 MCP 수집 |

---

## 빌더 SVG 차트 카탈로그 (32종, svg_radar 금지)

**Tier 1 — Core (11종)**: donut · bar · line · hbar · waterfall · scatter · football · heatmap · grouped_bar · bubble_risk · flow_diagram

**Tier 2 — Extended (16종)**: area · timeline · roe_pbr_path · rebased_price · candlestick · boxplot · bullet · gantt · pareto · bump · sparkline · lollipop · histogram · slope · tornado · treemap

**Tier 3 — Advanced (5종)**: sankey · waffle · gauge · marimekko · pictogram

> `svg_radar` 는 v13부터 금지. `svg_grouped_bar()` 또는 `svg_scatter()` 로 대체.

---

## 섹션별 최소 분량 (SECTION_MINIMA)

| # | 섹션 | 글자 | 차트 | 테이블 | counter_arg |
|:-:|---|---:|:-:|:-:|:-:|
| 1 | 기업개요 | 3,000 | 1+ | 2+ | - |
| 2 | 산업분석 | 10,000 | 4+ | 2+ | - |
| 3 | 투자포인트 I | 8,000 | 3+ | 1+ | **1+** |
| 4 | 투자포인트 II | 8,000 | 3+ | 1+ | **1+** |
| 5 | 투자포인트 III | 8,000 | 3+ | 1+ | **1+** |
| 6 | 재무분석 | 7,000 | 4+ | 4+ | - |
| 7 | Peer 비교 | 4,000 | 3+ | 3+ | - |
| 8 | 실적추정 | 7,000 | 3+ | 4+ | - |
| 9 | 밸류에이션 | 6,000 | 3+ | 3+ | - |
| 10 | 리스크 | 4,000 | 2+ | 1+ | **1+** |
| 11 | Appendix | 17,000 | 0 | 8+ | - |
| **합** | | **82,000** | **26+** | **30+** | **4+** |

---

## SMIC 문체 규칙 (Evaluator v2 기준)

- **'동사' 호칭**: 기업명 직접 사용 금지, 40회+ 사용
- **'본서는/본서에서는'**: 5회+ 사용
- **'전술한/후술할'**: 섹션 간 크로스레퍼런스, 5회+
- **볼드-첫문장**: 모든 단락 첫 문장 `<strong>` 처리, 150개+
- **전환어**: 전술한 / 그렇다면 / 이에 더해 / 한편 / 이처럼 / 실제로 / 다만 (30회+)
- **반박 2중 구조**: 인라인 반박(본문) + counter_arg 블록 (각 IP당 1+)

---

## 할루시네이션 패턴 (탐지 시 FAIL)

```
약 \d+%    |  대략 \d+      |  정도로? 추정
일반적으로 \d+  |  보통 \d+    |  통상적으로
업계 평균 \d+  |  약간        |  다소
```

**원칙**: 모든 숫자는 출처가 있어야 한다. 출처 없는 추정은 삭제.

---

## 개발 이력

- **v15.1** (2026-04-11) — builder/ 모듈 10개 + sections/ 14개 + phase65/rerating 구현
- **v15.0** (2026-04-11) — 표준화 전면 재설계, SKILL.md 75% 감축, 모듈 아키텍처 도입
- **v14.1** (2026-04-04) — Evaluator v2 ALL PASS 시스템 완성
- **v13.2** (2026-04-03) — Jeff Sun 기술적 분석 + KIS Backtest MCP
- **v10~v12** — SMIC 문체 정립, 서브에이전트 병렬 빌드
- **v7~v9** — 벤치마크 14건 종합, 89점 자동 달성

상세 이력: [CHANGELOG.md](CHANGELOG.md)

---

## 빌드 파이프라인 (Phase 0~7)

```
Phase 0  — Pre-flight 검증 (preflight_validate)
            ├─ F1 재무 드리프트 체크
            ├─ F2 주가 드리프트 체크 (F2_VOLATILITY → Re-rating Mode)
            ├─ F3 Triple check (PBR×BPS=Price)
            ├─ F4 원본 응답 저장
            └─ F5 산업 체크리스트
Phase 1  — MCP 데이터 수집 (DART/stocks/ECOS/backtest)
Phase 2  — 엑셀 시트 v1 빌드 (Single Source of Truth)
Phase 3  — IP 3개 초안 수립
Phase 4  — 본문 작성 (sections/ 11개 병렬 빌드)
Phase 5  — 엑셀 시트 v2 업데이트 (본문 수치 완전 기록)
Phase 6  — HTML 빌드 + Evaluator v2 ALL PASS 루프
Phase 6.5— 백테스트 검증 (run_phase65)
Phase 7  — (조건부) Re-rating Note v2 삽입 + SMIC 주입
```

---

## 사용 예시 (현대건설 000720, Re-rating Mode)

사례 기록: `SKILL.md` Appendix A `CASE-000720-v2`

```python
# Phase 0 Pre-flight 에서 주가 +370% 감지 → F2_VOLATILITY
from post_processing.rerating_note import ReratingNoteV2, RatingChange, gen_rerating_note_v2

note = ReratingNoteV2(
    fail_code="F2_VOLATILITY",
    trigger_summary="주가 +370% 급등 (1년), 빌더 기준가 33,500원 vs 실제 179,500원",
    changes=[
        RatingChange("투자의견", "BUY", "HOLD",
                     "리레이팅이 이미 가격에 반영됨"),
        RatingChange("목표주가", "45,000원", "200,000원",
                     "v1 EPS/PBR 가정 무효화"),
    ],
    new_investment_points=["중동 르네상스 수주", "1기 신도시 재건축"],
    new_bear_cases=["Kitchen Sinking 해소 지연", "PF 우발채무"],
    new_kill_conditions=["2025H2 영업이익 흑자 전환 실패"],
)
rerating_html = gen_rerating_note_v2(note)
# → builder.build_report() 의 post_process 에 주입하여 커버 직후 삽입
```

---

## 라이선스 / 기여

내부 사용 전용. CUFA 공식 보고서 생성에만 사용.
피드백·개선 제안은 `CHANGELOG.md` PR 로 제출.
