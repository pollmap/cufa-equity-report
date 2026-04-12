# CUFA Equity Report Skill v16.0

> **1인 AI 퀀트 운용사 실행 도구** — 학회 분량 페티시 완전 폐기, HF/퀀트 실행가능성 중심 전환.
> Nexus Finance MCP(398도구) → CUFA 보고서 → open-trading-api/QuantPipeline 선순환 파이프라인.

**핵심 원칙**: 보고서는 Trade Ticket으로 끝난다. Evaluator v3 12/12 ALL PASS = 배포 기준.

---

## What's New in v16

| 범주 | v15 (학회) | v16 (퀀트) |
|---|---|---|
| Evaluator | 분량 14개 (80K자/25SVG/동사40...) | **실행가능성 12개** binary |
| 섹션 | 11개 SMIC 구조 | **7섹션 HF 구조** |
| 문체 | 동사/본서/전술한 강제 | **자유 평서문** |
| 산출물 | HTML + Excel 16시트 | HTML + Excel **6시트** + **Trade Ticket YAML** |
| 피드백 | 없음 | **Phase 7 분기별 복기** |

---

## Quick Start

```python
from config._template import StockConfig
from preflight import preflight_validate, NexusMCPClient
from builder import build_report, write_output
from evaluator import evaluate
from trade_ticket import generate_trade_ticket, ticket_to_yaml, validate_trade_ticket
from sections import (
    build_section1, build_section2, build_section3,
    build_section4, build_section5, build_section6, build_section7,
)

# 1) StockConfig 작성 (v16 필드 포함)
config = StockConfig(
    stock_code="329180",
    company_name="HD한국조선해양",
    company_name_en="HD Korea Shipbuilding",
    market="KOSPI",
    industry="조선",
    subtitle="LNG 르네상스와 슬롯 희소성의 교차점",
    builder_revenue=25_100_000_000_000,
    builder_op_income=1_120_000_000_000,
    builder_price=475_000,
    builder_bps=275_000,
    builder_eps_next=32_000,
    shares_outstanding=48_500_000,
    target_year=2024,
    # v16 신규 필드
    trade_ticket={
        "opinion": "BUY",
        "entry_price": 475_000,
        "stop_loss": 410_000,
        "target_price": 528_750,
        "horizon_months": 12,
        "position_size_pct": 5.0,
    },
    kill_conditions=(
        "수주잔고 YoY -20% 이하로 붕괴",
        "강재 원가 YoY +40% 이상 + OPM 역전",
        "핵심 경쟁사 슬롯 잠식 (점유율 -10%p)",
    ),
    backtest_config={
        "engine": "open-trading-api/QuantPipeline",
        "benchmark": "KOSPI",
        "slippage_bps": 10,
    },
    feedback_loop={"enabled": True, "review_cycle_months": 3},
)

# 2) Phase 0 — Pre-flight 검증
result = preflight_validate(config, NexusMCPClient())
if result.has_fail():
    raise SystemExit(result.fail_codes)

# 3) 7섹션 HTML 빌드
ctx = build_report(
    config,
    section_builders=[
        build_section1, build_section2, build_section3,
        build_section4, build_section5, build_section6, build_section7,
    ],
    opinion="BUY",
    target_price=528_750,
    current_price=475_000,
)

# 4) Evaluator v3 — 12/12 ALL PASS 루프
ev_result = evaluate(ctx.output_html)
if not ev_result.all_passed:
    print(ev_result.format_report())  # 어느 체크가 실패했는지 확인
    # 수정 후 재빌드...

# 5) Trade Ticket YAML 생성
ticket = generate_trade_ticket(config)
errors = validate_trade_ticket(ticket)
assert not errors, errors
Path("output/HD한국조선해양_trade_ticket.yaml").write_text(ticket_to_yaml(ticket))

# 6) 저장
html_path = write_output(ctx, config)
print(f"Report: {html_path}")
# Evaluator: === Evaluator v3 — 12 / 12 PASS === ✅ ALL PASS
```

---

## 모듈 구조

```
cufa-equity-report/
├── SKILL.md                    ← 전체 프로토콜 (v16)
├── preflight/                  ← Phase 0: MCP 실데이터 검증
├── config/                     ← 종목별 StockConfig
├── builder/                    ← HTML 빌드 엔진
├── trade_ticket/               ← ⭐ v16 신규: Trade Ticket YAML 파이프라인
│   ├── schema.py               ← TradeTicket 스키마 + validate()
│   ├── generator.py            ← config → TradeTicket
│   ├── backtest_hook.py        ← open-trading-api/QuantPipeline 연동
│   └── feedback.py             ← Phase 7 복기 엔진
├── evaluator/                  ← v3 실행가능성 검증 (12 binary)
├── sections/                   ← 7섹션 HF 빌더
│   ├── section1_bluf.py        ← Investment Summary
│   ├── section2_thesis.py      ← 3축 Thesis
│   ├── section3_business_setup.py
│   ├── section4_numbers.py     ← Financial + Peer + Estimate + Valuation
│   ├── section5_risks.py       ← Bear Case First + Kill Conditions
│   ├── section6_trade.py       ← ⭐ Trade Implementation
│   └── section7_appendix.py
├── post_processing/            ← Re-rating Note v2
└── output/                     ← 생성 결과
    ├── {종목}_CUFA_보고서.html
    ├── {종목}_trade_ticket.yaml ← ⭐ v16 신규
    └── data/backtest/           ← QuantPipeline 결과
```

---

## Evaluator v3 — 12개 실행가능성 체크

```
=== Evaluator v3 — 12 / 12 PASS === ✅ ALL PASS
  [PASS] opinion                 BUY/HOLD/SELL 명시
  [PASS] target_price            목표주가 확인
  [PASS] stop_loss               손절가 확인
  [PASS] position_size           포지션 비중 확인
  [PASS] bear_floor              Bear Case 하방 확인
  [PASS] kill_conditions         Kill Condition 3건 ≥ 3
  [PASS] catalyst_timeline       Catalyst 3건 ≥ 3
  [PASS] trade_ticket            Trade Ticket 확인
  [PASS] data_sources            데이터 출처 확인
  [PASS] backtest_hook           Backtest 연동 확인
  [PASS] falsifiable_thesis      반증 조건 확인
  [PASS] risk_reward             R/R 수치 확인
```

---

## 7섹션 HF 구조

| # | 섹션 | 핵심 |
|---|---|---|
| §1 | Investment Summary (BLUF) | 이 섹션만 읽어도 투자판단 가능 |
| §2 | 투자 Thesis | 3축 논리 + 반증 조건 |
| §3 | Business & Industry Setup | 사업구조 + 산업 포지셔닝 |
| §4 | The Numbers | 재무+Peer+추정+밸류 통합 |
| §5 | Risks — Bear Case First | Bear 먼저, Kill Conditions 3+개 |
| §6 | Trade Implementation | Trade Ticket YAML + QuantPipeline |
| §7 | Appendix | 재무3표 + Peer + DCF가정 + 출처 |

---

## Phase 파이프라인

```
Phase 0: Pre-flight (MCP 실호출)
Phase 1: 리서치 + config.py
Phase 2: Excel 6시트
Phase 3: 투자포인트 3개 + Kill 3개 [게이트: 사용자 승인]
Phase 4: 7섹션 본문
Phase 5: Excel 최종화
Phase 6: HTML 빌드 + Evaluator v3 ALL PASS + Trade Ticket YAML
Phase 6.5: QuantPipeline 백테스트 (선택)
Phase 7: 분기별 복기 (actual vs estimated)
```

---

## Industry Checklist (v16 조선 추가)

조선/해운/건설/제조/금융/바이오/IT 9종 산업 체크리스트.
`preflight/industry_checklist.py` 참조.

---

## 레거시 백업

- `SKILL_legacy_v15_backup.md` — v15.2 (2026-04-11)
- `SKILL_legacy_v14_2_backup.md` — v14.2 (2026-04-11)
