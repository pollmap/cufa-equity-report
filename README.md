# CUFA Equity Research Report System

**AI 기반 기업분석보고서 완전 자동화 시스템** -- 충북대학교 가치투자학회(CUFA)

원커맨드 하나로 **HTML 보고서 + 엑셀 재무데이터 + 마크다운 본문 + GitHub push** 전부 자동.

> "모든 숫자에는 출처가 있고, 모든 가정에는 반증 조건이 있다."

---

## Quick Start

```bash
git clone https://github.com/pollmap/cufa-equity-report.git
cd cufa-equity-report
pip install openpyxl pandas requests pykrx

# 신규 종목 (Phase 0 데이터 수집부터 전체 자동)
python run.py 삼성전자 005930 --collect

# 기존 종목 재빌드 (config.py 있을 때)
python run.py 삼성전자

# 매년 실적 업데이트
python run.py 삼성전자 --update

# 빌드 가능 종목 목록
python run.py --list
```

---

## 산출물 3종 (모두 자동 생성)

| 산출물 | 파일 | 용도 |
|--------|------|------|
| HTML 보고서 | {종목}\_CUFA\_보고서.html | 인터랙티브 다크테마, SVG 25+, Float TOC |
| 엑셀 재무데이터 | {종목}\_재무데이터.xlsx | 10시트 (IS/BS/CF/Peer/DCF 등) |
| 마크다운 본문 | {종목}\_CUFA\_본문.md | AI 편집/가공/이해 최적화 |

---

## 전체 파이프라인

```
python run.py {종목} {코드} --collect

  Phase 0  데이터 수집 (data/collector.py)
    1순위  Nexus MCP DART   재무제표 5개년 CFS + 주가 + 금리
    2순위  pykrx (KRX)      주가 52주 고저 + 거래량
    3순위  FnGuide          IS/BS/CF HTML 파싱
    4순위  TODO 주석         수동 입력 대기 (Mock 금지!)

  Phase 1  config.py 자동 생성 (Single Source of Truth)

  Phase 2  builder/build.py  HTML 보고서 생성
           sections.py 있으면 커스텀 본문 반영
           template/style.css HD건설기계 v4-1 표준

  Phase 3  builder/evaluator.py  품질 자동 검증
           HARD_MIN + SMIC_STYLE + HALLUCINATION + SECTION_CHARS

  Phase 4  build_xlsx.py  엑셀 10시트 생성

  Phase 5  git add + commit + push  GitHub 자동
```

---

## 시스템 계층 구조

```
Layer 0  run.py              원커맨드 오케스트레이터
Layer 1  data/collector.py   Nexus MCP + pykrx + FnGuide Fallback
Layer 2  config.py           Single Source of Truth (연도 자동)
Layer 3  builder/build.py    HTML 생성 + template/style.css
Layer 4  evaluator.py        Evaluator v2 품질 검증
Layer 5  output/             HTML + Excel + Markdown + GitHub
```

---

## 보고서 논리 흐름

```
커버     이 회사, 지금 사야 하나?
         투자의견 + 목표주가 + 업사이드 + IP 3개 한줄 요약

[배경]   Sec 1   기업개요    이 회사가 뭐 하는 회사인가?
         Sec 2   산업분석    이 산업 지금 어디에 있나?
         Sec 2-1 기업분석    이 회사의 포지션은?

[논거]   Sec 3   IP 1       5단계 추론체인 + 2중 counter_arg
         Sec 4   IP 2       5단계 추론체인 + 2중 counter_arg
         Sec 5   IP 3       5단계 추론체인 + 2중 counter_arg

[검증]   Sec 6   재무분석    듀폰/ROIC/OCF/FCF
         Sec 7   Peer비교   OPM x PER 산점도
         Sec 8   실적추정    P x Q Bottom-up + 시나리오
         Sec 9   밸류에이션  WACC + Football Field + DCF히트맵

[관리]   Sec 10  리스크      Kill Conditions + Catalyst Timeline
         Sec 11  Appendix   A-1 ~ A-16
```

---

## IP 5단계 추론 방법론 (SMIC S등급)

```
B등급  산업성장 -> 주가상승 (2단계)
A등급  수요 -> 매출 -> OPM -> EPS (3~4단계)
S등급  트렌드 -> 카테고리 -> 포지셔닝 -> 수익영향 -> 밸류에이션리레이팅 (5단계)

예시 (삼성전자 HBM):
  AI인프라투자 -> HBM GPU당 2배증가 -> 삼성점유율25->35% -> DS OPM 30%+ -> PER재평가
```

각 IP마다 2중 반박 구조 필수:
- 인라인 반박: "다만 ~우려 -> 1 2 3 반박"
- counter_arg 블록: 시장의 우려 vs 정량적 반박

---

## Evaluator v2 품질 기준

| 카테고리 | 항목 | 기준 |
|----------|------|------|
| HARD_MIN | 텍스트 | 80,000자+ |
| HARD_MIN | SVG 차트 | 25개+ |
| HARD_MIN | 테이블 | 25개+ |
| HARD_MIN | H2/H3 | 20개+ |
| SMIC_STYLE | 볼드 첫문장 | 150개+ |
| SMIC_STYLE | 평균 문단 | 150~450자 |
| SMIC_STYLE | 크로스레퍼런스 | 5회+ |
| SMIC_STYLE | "동사" 호칭 | 40~120회 |
| SMIC_STYLE | 전환어 | 30회+ |
| SMIC_STYLE | counter_arg | 3개+ |
| HALLUCINATION | "약 N%" 등 | 0건 목표 |

---

## config.py 핵심 포맷

```python
TICKER        = "005930"
COMPANY_NAME  = "삼성전자"
CURRENT_PRICE = 210_000           # 원
MARKET_CAP    = 12_536_543        # 억원 (주가 x 주식수 / 1억)

FINANCIALS = {
    "revenue": {2023: 2_589_355, 2024: 3_008_709, 2025: 3_336_059,
                "2026E": 3_607_000, "2027E": 3_918_000},
}

RATIOS = {"psr_ttm": 3.76, "per_ttm": 32.0, "pbr": 3.28, "roe": 10.4}

PRODUCTS = [{"name": "DS", "revenue_pct": 33, "description": "..."}]
PEERS = {"000660": {"name": "SK하이닉스", "per": 12.0, "opm": 38.0}}
RISKS = [{"name": "HBM열위", "probability": 30, "impact": 70}]
KILL_CONDITIONS = [{"condition": "OPM<8%", "current": "13.1%", "margin": "5.1%p", "frequency": "분기별"}]
INVESTMENT_POINTS = [
    {"id": 1, "title": "HBM4 마진 재편", "subtitle": "...",
     "chain": ["AI수요", "HBM폭증", "점유율회복", "OPM개선", "PER리레이팅"]}
]
```

---

## sections.py API

```python
C = None  # build.py가 mod.C = C 로 주입

def gen_section1() -> str:
    header = C.section_header(1, "기업 개요", "삼성전자", "005930")
    body   = C.sidebar_wrap([("설립","1969년")], "<p><strong>볼드.</strong> 본문</p>")
    chart  = C.add_source(C.svg_bar("매출", labels, vals, sec=1), "DART")
    return header + body + chart
```

C 모듈 주요 함수: section_header, sidebar_wrap, table, svg_bar, svg_line, svg_donut, svg_scatter, svg_football, svg_heatmap, svg_timeline, add_source, counter_arg, callout, expand_card

---

## 연도 자동 전환

REPORT_YEAR = datetime.now(KST).year -- 매년 자동.

| 연도 | EST_YEARS | ACTUAL_YEARS |
|------|-----------|--------------|
| 2026 | 2026E, 2027E, 2028E | 2025A, 2024A, 2023A |
| 2027 | 2027E, 2028E, 2029E | 2026A, 2025A, 2024A |

---

## 현황 (2026-04-08)

| 종목 | 의견 | 현재가 | 목표주가 | HTML |
|------|------|--------|----------|------|
| 삼성전자 (005930) | BUY | 210,000 | 250,000 | 317KB |
| 인텔리안테크 (189300) | BUY | 111,200 | 155,000 | 346KB |
| 이노스페이스 (462350) | - | - | - | 335KB |

---

## 파일 구조

```
cufa-equity-report/
  run.py                     원커맨드 오케스트레이터
  data/collector.py          Phase 0 자동수집 (MCP + Fallback)
  builder/build.py           HTML 생성 엔진
  builder/evaluator.py       Evaluator v2
  template/style.css         HD건설기계 v4-1 (수정 금지!)
  template/components.py     C 모듈 26개 함수
  template/interactive.js    Float TOC, 진행률 바
  examples/삼성전자/          config.py + sections.py + build_xlsx.py
  examples/인텔리안테크/      config.py + sections.py + build_xlsx.py
  examples/이노스페이스/      config.py + build_xlsx.py
  output/                    .gitignore (HTML + Excel 로컬)
```

---

## 핵심 원칙

| 원칙 | 내용 |
|------|------|
| Mock 금지 | 수집 실패 -> TODO 주석. 가짜 데이터 절대 금지 |
| CSS 고정 | template/style.css 절대 수정 금지 |
| 3종 산출물 | HTML + 엑셀 + 마크다운. 셋 다 필수 |
| 연도 자동화 | datetime.now().year로 자동 전환 |
| 결정론적 숫자 | 입력 -> 수학 -> 출력. 모든 수치에 출처 |
| 반증 가능성 | Kill Condition 명시. 틀렸을 때 추적 가능 |

---

MIT License -- 충북대학교 가치투자학회(CUFA)

> AI 도구(Claude Code + Nexus MCP)가 수집/작성을 보조.
> 투자 판단과 최종 검증은 학회원이 수행합니다.
> 본 시스템이 생성하는 보고서는 매수/매도 권유가 아닙니다.
