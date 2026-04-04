# CUFA Equity Research Report System

**AI 기반 기업분석보고서 자동 생성 시스템** — 충북대학교 가치투자학회(CUFA)

어떤 종목이든 **동일한 품질**의 인터랙티브 HTML 보고서를 생성하는 범용 도구.
config.py(데이터) + sections.py(본문)만 작성하면, 시스템이 SMIC급 보고서를 자동 빌드+검증한다.

> **"모든 숫자에는 출처가 있고, 모든 가정에는 반증 조건이 있다."**

## 핵심 가치

| 원칙 | 설명 |
|------|------|
| **결정론적 숫자** | AI가 숫자를 "창의적으로" 만들지 않는다. 입력→수학→출력. 모든 수치에 출처 필수 |
| **반증 가능성** | 모든 가정에 Kill Condition(반증 조건)이 있다. 틀렸을 때 추적 가능 |
| **확률적 추론** | Bull 25% / Base 50% / Bear 25%. 정답이 아닌 확률 분포 |
| **재현 가능** | 누구든(다른 AI든) 같은 config → 같은 품질의 보고서 |

## Features

- **인터랙티브 HTML** — 다크 테마, SVG 차트 40+, Float TOC, 진행률 바, 접기/펼치기
- **SMIC 문체 자동 강제** — 볼드 첫문장 150+, 전환어 90+, 크로스레퍼런스 5+, 동사 호칭
- **4중 밸류에이션** — PSR/PER + DCF + Reverse DCF + Football Field 크로스체크
- **Kill Conditions** — 투자논지 사망 조건 명시 + 신호등 시각화
- **Evaluator v2** — 자동 품질 검증 (HARD_MIN + SMIC_STYLE + 할루시네이션 탐지 + 섹션별 글자수)
- **KIS 백테스트 연동** — 투자포인트 → 매매전략 YAML → KIS MCP 백테스트
- **Executive Summary** — 커버 직후 핵심 수치 + Bull/Base/Bear 요약

## Quick Start

```bash
# 1. 클론
git clone https://github.com/pollmap/cufa-equity-report.git
cd cufa-equity-report

# 2. 종목 config 작성 (템플릿 복사)
mkdir -p examples/종목명
cp data/templates/config_template.py examples/종목명/config.py
# → config.py에 재무데이터, 주가, IP, Kill Conditions 등 채우기

# 3. (선택) 커스텀 본문 작성
cp examples/이노스페이스/sections.py examples/종목명/sections.py
# → sections.py에서 gen_section1()~gen_section11() 수정

# 4. 보고서 빌드
python builder/build.py examples/종목명/config.py

# 5. 품질 검증
python builder/evaluator.py output/종목명_CUFA_보고서.html

# 6. 상세 문체 리포트
python builder/evaluator.py output/종목명_CUFA_보고서.html --style-report

# 7. 브라우저에서 확인
start output/종목명_CUFA_보고서.html
```

## Architecture

```
cufa-equity-report/
├── template/                   # 디자인 시스템 (절대 표준)
│   ├── style.css               # HD건설기계 v4-1 CSS (수정 금지!)
│   ├── style_extended.css      # CUFA 추가 컴포넌트 CSS
│   ├── components.py           # SVG 15종 + 테이블 + 레이아웃 함수
│   └── interactive.js          # Float TOC, progress bar, expand toggle
│
├── builder/                    # 빌드 엔진
│   ├── build.py                # 메인 빌드 (config → HTML 조립)
│   └── evaluator.py            # 품질 검증 v2 (HARD_MIN + SMIC + 할루시네이션)
│
├── data/
│   └── templates/
│       └── config_template.py  # 종목별 config 템플릿
│
├── trading/                    # KIS 백테스트 연동
│   ├── strategy_extractor.py   # IP → 매매전략 YAML 변환
│   └── backtest_runner.py      # KIS MCP (127.0.0.1:3846) 연동
│
├── examples/                   # 종목별 예시 (검증 완료)
│   └── 이노스페이스/
│       ├── config.py           # 데이터 (재무, 주가, IP, Kill Conditions)
│       └── sections.py         # 커스텀 본문 (11개 섹션)
│
└── docs/
    └── MCP_INTEGRATION.md      # Nexus MCP 통합 설계 문서
```

## 빌드 플로우

```
config.py (데이터)
    │
    ▼
build.py ─── style.css + style_extended.css (CSS)
    │    ├── components.py (SVG/테이블/레이아웃)
    │    ├── sections.py (커스텀 본문, 있으면 로드)
    │    └── interactive.js (인터랙티브 기능)
    │
    ▼
output/종목명_CUFA_보고서.html
    │
    ▼
evaluator.py ─── ALL PASS? → 완료!
                  FAIL?    → 어디가 부족한지 정확히 진단
```

### sections.py 플러그인 시스템

config.py 옆에 `sections.py`가 있으면 자동 로드. 없으면 build.py가 스켈레톤(22K chars)을 자동 생성.

```python
# sections.py 구조
C = None  # build.py가 components 모듈 주입

def gen_section1() -> str:
    """섹션 1: 기업 개요"""
    header = C.section_header(1, "기업 개요", "종목명", "코드")
    sb = C.sidebar_wrap([("핵심", "키워드")], '<p>본문...</p>')
    chart = C.svg_bar("차트 제목", ["A", "B"], [10, 20], sec=1)
    return f'<div class="section" id="sec1">{header}{sb}{chart}</div>'

# gen_section2() ~ gen_section11() 동일 패턴
```

## 보고서 구조 (11개 섹션)

| # | 섹션 | 내용 | 최소 글자수 |
|:-:|------|------|:----------:|
| 1 | 기업 개요 | 사업 소개, 주주, 연혁 | 3,000 |
| 2 | 산업 분석 | TAM/SAM/SOM, 경쟁 구도, 진입장벽 | 10,000 |
| 3 | 투자포인트 ① | 핵심 IP + 반박 통합 | 4,000 |
| 4 | 투자포인트 ② | 2번째 IP + 반박 통합 | 4,000 |
| 5 | Plus Alpha | 추가 카탈리스트 | 4,000 |
| 6 | 재무 분석 | IS/BS/CF 분석, 유증 희석 | 5,000 |
| 7 | 비용 분석 | R&D, Burn Rate, BEP | 3,000 |
| 8 | 실적 추정 | P×Q 모델, Bull/Base/Bear 시나리오 | 5,000 |
| 9 | 밸류에이션 | PSR/DCF/Reverse DCF/Football Field | 4,000 |
| 10 | 리스크 분석 | 5대 리스크 + Kill Conditions | 3,000 |
| 11 | Appendix | 재무제표, 가정 추적 테이블 | 2,000 |

## Evaluator v2 — 자동 품질 검증

```bash
python builder/evaluator.py output/보고서.html
```

### 검증 항목

| 카테고리 | 항목 | 기준 | 설명 |
|---------|------|:----:|------|
| **HARD_MIN** | text_80k | 80,000자+ | 본문 텍스트 총량 |
| | svg_25 | 25개+ | SVG 차트 수 |
| | tables_25 | 25개+ | 테이블 수 |
| | h2h3_20 | 20개+ | 소제목 수 |
| **SMIC_STYLE** | bold_first_150 | 150개+ | `<p><strong>` 볼드 첫문장 |
| | avg_para_len | 150~450자 | 문단 평균 길이 |
| | cross_ref_5 | 5개+ | "전술한/후술할" 크로스레퍼런스 |
| | dongsa_ratio | 40~120 | "동사" 호칭 횟수 |
| | transitions_30 | 30개+ | 전환어 ("한편", "이에 더해" 등) |
| | counter_args_3 | 3개+ | 반박 논파 블록 |
| | callout_3 | 3개+ | KEY TAKEAWAY 블록 |
| **HALLUCINATION** | 패턴 탐지 | 0건 | "약 N%", "대략", "정도로 추정" 등 |
| **SECTION_CHARS** | sec1~sec11 | 개별 기준 | 섹션별 최소 글자수 |

### --style-report 모드

```bash
python builder/evaluator.py output/보고서.html --style-report
# → [WARN] sec3 단락 5: bold 첫문장 없음 — "소형발사체 시장은..."
# → [WARN] sec6 단락 2: bold 첫문장 없음 — "매출 구조를 살펴보면..."
# → 총 45개 단락 중 22개 미준수 (49%)
```

## components.py — SVG 차트 15종

| 함수 | 용도 | 시그니처 |
|------|------|---------|
| `svg_bar` | 수직 막대 | `(title, labels, values, sec)` |
| `svg_hbar` | 수평 막대 | `(title, labels, values, sec)` |
| `svg_line` | 선 차트 | `(title, labels, datasets=[(name, values, color)], sec)` |
| `svg_donut` | 도넛 | `(title, segments=[(label, value, color)], sec)` |
| `svg_waterfall` | 워터폴 | `(title, items=[(label, delta)], sec)` |
| `svg_scatter` | 산점도 | `(title, points=[(x, y, label)], sec)` |
| `svg_football` | 풋볼 필드 | `(title, rows=[(label, lo, hi, color)], current, sec)` |
| `svg_heatmap` | 히트맵 | `(title, rows, cols, values, sec)` |
| `svg_grouped_bar` | 그룹 막대 | `(title, labels, datasets, sec)` |
| `svg_bubble_risk` | 버블 리스크 | `(title, risks=[(label, prob, impact, severity)], sec)` |
| `svg_per_band` | PER 밴드 | `(title, years, price, bands, sec)` |
| `svg_area` | 영역 차트 | `(title, labels, datasets, sec)` |
| `svg_flow_diagram` | 플로우 | `(title, nodes, flows, sec)` |
| `svg_timeline` | 타임라인 | `(title, events, sec)` |
| `svg_annotated_price` | 주가 주석 | `(title, dates, prices, annotations, sec)` |

### 레이아웃 컴포넌트

| 함수 | 용도 |
|------|------|
| `section_header(num, title, stock_name, stock_code)` | 섹션 헤더 |
| `sidebar_wrap(kv_pairs, content_html)` | 사이드바 + 본문 2열 레이아웃 |
| `table(headers, rows, sec, title, src)` | 데이터 테이블 |
| `counter_arg(concern, rebuttal)` | 반박 논파 박스 |
| `callout(text)` | KEY TAKEAWAY 블록 |
| `chart_with_insight(chart_html, insight, src)` | 차트 + 해석 블록 |
| `chart_pair(chart1, chart2)` | 2열 차트 배치 |
| `metric_grid(metrics)` | 4열 지표 카드 |
| `scenario_grid(scenarios)` | Bull/Base/Bear 3열 |
| `kill_condition_gauge(conditions)` | Kill Condition 신호등 |
| `assumption_tracker(assumptions)` | 가정 추적 테이블 |

## Design System

| 변수 | 값 | 용도 |
|------|-----|------|
| `--bg` | `#0D0D1A` | 배경 |
| `--card-bg` | `#161628` | 카드/차트 배경 |
| `--purple` | `#7C6AF7` | 시그니처 (동사/핵심) |
| `--green` | `#00E09E` | 상승/긍정 |
| `--red` | `#FF4D4D` | 하락/부정 |
| `--text` | `#E8E6F0` | 본문 텍스트 |
| `--text-sec` | `#A09CB0` | 보조 텍스트 |

**style.css** = HD건설기계 v4-1에서 추출한 검증된 표준. **절대 수정 금지.**
**style_extended.css** = CUFA 고유 컴포넌트(counter-arg, callout, expand, float-toc 등).

## SMIC 문체 규칙

Evaluator가 자동 검증하는 문체 기준 (서울대 SMIC 4편 역설계):

| 규칙 | 설명 | 예시 |
|------|------|------|
| **동사 호칭** | 기업을 "동사"로 지칭 | "동사는 TC2C 공정이 완성될 경우~" |
| **볼드 첫문장** | 모든 단락 첫 문장 `<strong>` | "**정유사는 고도화 설비 도입을 늘리고 있다.** ~" |
| **전환어 7종** | 전술한/그렇다면/이에 더해/한편/이처럼/실제로/다만 | |
| **크로스레퍼런스** | "전술한/후술할"로 섹션 간 연결 | "[투자포인트 1]에서 전술한 것처럼~" |
| **반박 이중구조** | 인라인 반박 + counter_arg 블록 | IP당 최소 2건 |
| **원문자 나열** | ①②③으로 복수 논점 정리 | |

## 검증 완료 보고서

### 이노스페이스 (462350) — ALL PASS

```
Text: 80,002 chars | SVG: 40 | Tables: 40
bold_first: 154 | cross_ref: 5 | dongsa: 117 | transitions: 92
11개 섹션 전부 PASS
```

## 다른 AI에서 사용하기

이 시스템은 **어떤 AI(Claude, GPT, Gemini 등)에서든 일관된 결과**를 만들도록 설계됐다:

1. **config.py가 Single Source of Truth** — AI가 숫자를 "창의적으로" 만들 여지 없음
2. **components.py가 API 강제** — `C.svg_bar()`, `C.table()` 등 정해진 함수만 사용
3. **evaluator.py가 품질 강제** — ALL PASS가 아니면 어디가 부족한지 정확히 진단
4. **sections.py 패턴이 명확** — `gen_section1()~gen_section11()` 구조 고정

### AI에게 줄 프롬프트 예시

```
이 레포를 클론해서 {종목명}의 보고서를 만들어줘:
https://github.com/pollmap/cufa-equity-report

1. examples/이노스페이스/config.py를 참고해서 examples/{종목명}/config.py 작성
2. examples/이노스페이스/sections.py를 참고해서 examples/{종목명}/sections.py 작성
3. python builder/build.py examples/{종목명}/config.py 실행
4. python builder/evaluator.py output/{종목명}_CUFA_보고서.html 실행
5. ALL PASS가 나올 때까지 반복 수정
```

## License

MIT License

## Credits

- **CUFA** (충북대학교 가치투자학회) — 투자 분석 방법론 + 철학
- **Luxon AI** — AI 인프라 + MCP 도구
- **SMIC/YIG/STAR** — 벤치마크 레퍼런스 (15편 역설계)
