---
name: cufa-equity-report
description: "CUFA 가치투자학회 기업분석보고서 생성 (v14.1). Evaluator v2로 품질 자동 검증. HD건설기계 v4-1 표준 CSS + SVG 15종 인라인 차트. GitHub: pollmap/cufa-equity-report. 트리거: '기업분석보고서', 'CUFA 보고서', '투자보고서', 'equity research', 'SMIC 스타일', '기업 리서치'. config.py → build.py → evaluator.py ALL PASS."
---

# CUFA 기업분석보고서 생성 스킬

## 투자분석의 본질 (v9 철학)

투자분석 보고서의 목적은 **주가를 맞히는 것이 아니다.**
미래를 정확히 예측하는 마법도, 정답을 찍는 도구도 아니다.

**이것은 확률적 추론 프레임워크다:**
- 정량 데이터로 **확률을 높이는** 과학적·통계적·정량적 연구 방법
- 맞히더라도 벌지 못할 수 있고, 틀리더라도 벌 수 있다
- 핵심은 **반증 가능성**: 모든 가정은 검증 가능해야 하고, 틀렸을 때 어디서 틀렸는지 추적 가능해야 한다
- 성공하면 성공의 원인을, 실패하면 실패의 원인을 정량적으로 복기한다

**따라서 보고서의 모든 주장은:**
1. 반드시 **정량적 근거**가 있어야 한다 (뇌피셜 = 실패)
2. 근거의 **출처**가 명시되어야 한다 (추적 가능성)
3. **반증 조건**이 제시되어야 한다 (어떤 수치가 나오면 이 가정이 틀린 건지)
4. **확률**로 표현되어야 한다 (Bull 25%/Base 50%/Bear 25%)
5. 사후 **복기 가능**해야 한다 (엑셀에 모든 가정과 데이터 저장)

## LLM 할루시네이션 방지 — 결정론적 숫자 원칙 (최우선)

**LLM(AI)은 숫자를 "그럴듯하게" 만들어내는 본능이 있다. 이것이 투자분석에서 가장 위험한 문제다.**

### 절대 금지: AI가 숫자를 생성하는 행위

```
× β = 1.2 (느낌으로)           → ○ β = 1.17 (출처: KRX 60개월 주간수익률 회귀, pykrx)
× 매출 성장률 15% (적당히)     → ○ 매출 성장률 14.7% (출처: 과거 5년 CAGR 12.3% + ASP 인상 2.4%)
× 영구성장률 2% (보통 그러니까) → ○ 영구성장률 1.8% (출처: 한국 명목GDP 성장률 10년 평균, ECOS)
× WACC 10% (대략)             → ○ WACC 9.87% (Ke 11.2%×E/(D+E) + Kd 4.5%×(1-t)×D/(D+E))
× OPM 개선 예상               → ○ OPM 12.3%→13.1% (원재료비 -0.5%p: 팜유 가격 CBOT 기준, 인건비 +0.3%p: 최저임금 인상률)
```

### 모든 숫자의 출처 체계

| 숫자 유형 | 반드시 따라야 할 방식 | 금지 |
|---------|-------------------|------|
| **과거 실적** | DART/FnGuide에서 가져온 확정값 | AI가 기억에서 꺼내기 |
| **주가/시총** | pykrx/KRX에서 당일 종가 | "대략 X만원" |
| **베타(β)** | KRX 또는 Bloomberg 60M 주간 회귀 | "보통 1.0~1.5" |
| **무위험이자율(Rf)** | 국고채 3년물 (ECOS 당일) | "3.5% 정도" |
| **ERP** | Damodaran 한국 ERP (연간 업데이트) | "6% 적용" |
| **매출 추정** | P×Q 분해 → 각 변수 근거 명시 | "15% 성장 예상" |
| **원가 추정** | 계정과목별 % of sales (과거 3년 추세 기반) | "원가율 유지 가정" |
| **성장률** | 과거 CAGR, 산업 보고서, 회귀분석 | "높은 성장 전망" |
| **Target Multiple** | Peer 평균/중앙값 + 프리미엄/디스카운트 근거 | "PER 15배 적용" |
| **영구성장률** | 명목GDP 성장률 또는 산업 장기 성장률 (출처 필수) | "2% 가정" |

### Evaluator 자동 검증

```python
# 할루시네이션 탐지 패턴
HALLUCINATION_PATTERNS = [
    r'약 \d+%',           # "약 15%" → 정확한 수치로
    r'대략 \d+',          # "대략 1조" → 정확한 값으로
    r'정도로? 추정',       # "15% 정도로 추정" → 출처+근거
    r'일반적으로 \d+',     # "일반적으로 10%" → 구체적 출처
    r'보통 \d+',          # "보통 PER 15배" → Peer 데이터
    r'통상적으로',         # 통상적 = 근거 없음
    r'업계 평균 \d+',     # "업계 평균" → 어떤 기관의 몇 년도 데이터?
]

for pattern in HALLUCINATION_PATTERNS:
    matches = re.findall(pattern, html)
    if matches:
        print(f'⚠ 할루시네이션 의심: {matches}')
```

### 결정론적 파이프라인

```
1. 데이터 수집: MCP에서 가져온 원본 숫자만 사용
2. 가공: 수학적 공식으로만 변환 (사칙연산, 회귀, 할인)
3. 가정: 모든 가정에 "왜 이 수치인지" + 출처 명시
4. 검증: 가정 변경 시 결과가 어떻게 바뀌는지 민감도 테이블
5. 기록: 엑셀 "데이터출처" 시트에 모든 숫자의 원본과 가공 과정 기록
```

**핵심: AI는 계산기(calculator)처럼 작동해야 한다. 입력값이 확정되면 출력값은 결정론적(deterministic)이어야 한다. AI가 "창의적으로" 숫자를 만드는 순간 보고서는 실패다.**

## 보고서의 존재 이유 — 모든 요소의 판단 기준 (v9 최우선 원칙)

**모든 글자, 모든 차트, 모든 테이블은 하나의 질문으로 판단한다:**
> "이걸 빼면 독자가 투자 판단을 내리는 데 지장이 있는가?"
> YES → 남긴다. NO → 삭제한다.

### 분량을 위한 분량 금지
- 60,000자 기준은 "최소한 이만큼은 있어야 충분히 설명 가능하다"는 의미이지, "60K 채우기" 게임이 아니다
- 55,000자인데 모든 내용이 밀도 있고 필요하면 55,000자가 맞다
- 60,000자인데 5,000자가 ESG 일반론이면 그건 55,000자보다 못하다

### 시각화를 위한 시각화 금지
- SVG 50개 기준은 "이 종목을 충분히 분석하려면 이만큼의 데이터 포인트가 필요하다"는 의미
- 차트 하나하나가 반드시 **하나의 메시지**를 전달해야 한다
- 메시지 없이 예쁘기만 한 차트 = 삭제 대상
- 차트마다 **"이 차트가 말하려는 것은 ___이다"**를 1문장으로 못 쓰면 그 차트는 불필요

### 전략적 구성
- 모든 섹션은 **독자의 사고 흐름**을 따라 배치
- 산업 이해 → 기업 이해 → 왜 투자해야 하는지 → 얼마에 사야 하는지 → 뭐가 잘못될 수 있는지
- 이 흐름을 벗어나는 내용은 아무리 좋아도 배치가 잘못된 것

### 직관적
- 차트를 보고 3초 안에 핵심 메시지를 파악할 수 있어야 한다
- 테이블을 보고 5초 안에 "어떤 숫자가 중요한지" 알 수 있어야 한다
- 사이드바를 읽으면 본문을 안 읽어도 전체 흐름이 잡혀야 한다

### 정직
- 모르면 모른다고 쓴다. 추정이면 추정이라고 쓴다. 불확실하면 확률로 표현한다.
- 불리한 데이터를 숨기지 않는다. Bear case를 약하게 쓰지 않는다.
- 목표주가가 현재가보다 낮으면 SELL이다. BUY 편향에 끌려가지 않는다.
- "정직한 보고서가 틀려도, 거짓된 보고서가 맞는 것보다 낫다."

## CUFA 리서치의 정체성 — "AI 시대에 살아남는 리서치"

AI가 보편화되면 누구나 보고서를 찍어낼 수 있다. 그때 CUFA가 살아남으려면:

### 해자 1: 데이터 → 판단의 간극을 메우는 능력
- AI는 데이터를 모을 수 있지만, **"이 데이터가 이 기업에 무슨 의미인지"**를 판단하는 건 사람이다
- CUFA 보고서의 가치는 숫자 나열이 아니라 **숫자 뒤의 인과관계를 추론하고 검증하는 과정** 자체에 있다
- 같은 DART 데이터를 보고도 "왜 이 OPM이 내년에 개선되는지"를 4단계 추론 체인으로 설명할 수 있어야 한다

### 해자 2: 반증 가능한 투자 논리
- 대부분의 AI 보고서는 "~할 것으로 전망된다"로 끝난다. 틀려도 추적이 안 된다
- CUFA는 **모든 가정에 반증 조건을 붙인다**: "만약 OPM이 11% 이하로 떨어지면 이 투자포인트는 무효"
- 6개월 후 복기할 때 "어디서 맞았고 어디서 틀렸는지"를 정량적으로 추적할 수 있는 보고서
- 이건 AI가 아무리 발전해도 **판단의 책임을 지는 사람**만 할 수 있다

### 해자 3: 엑셀 데이터셋의 재사용 가치
- 보고서 HTML은 읽히고 끝이지만, **엑셀은 살아있는 모델**이다
- 가정을 바꾸면 새로운 시나리오를 돌릴 수 있고, 팀원이 독립적으로 검증할 수 있다
- 투자 결정 후에도 실적 발표 때마다 엑셀을 업데이트하며 추적 가능
- **보고서 = 1회성 산출물, 엑셀 = 지속적 투자 도구** → 이 조합이 CUFA의 차별화

### 해자 4: 인터랙티브 + 반응형
- PDF는 죽어있다. CUFA의 HTML 보고서는 **살아있다**
- 클릭하면 상세가 열리고, 민감도를 직접 조작하고, 모바일에서도 읽힌다
- 이건 기술적 해자가 아니라 **독자 경험의 해자** — 한번 인터랙티브를 쓰면 PDF로 못 돌아간다

### 본질: 충북대학교 가치투자학회의 연구보고서
- CUFA 보고서는 **영리 목적이 아니다**. 투자 판단에 영향을 주기 위한 문서도 아니다
- 이것은 **학회원이 투자 분석 역량을 훈련하고, 그 과정을 기록한 연구보고서**다
- 연구의 가치는 "맞혔느냐"가 아니라 "방법론이 타당했느냐, 과정이 투명했느냐"에 있다
- 그래서 정직이 최우선이고, 반증 가능성이 핵심이고, 복기 가능한 엑셀이 필수인 것이다

### 브랜딩: "CUFA = 검증 가능한 투자 연구"
- 슬로건: **"모든 숫자에는 출처가 있고, 모든 가정에는 반증 조건이 있다"**
- CUFA 보고서를 읽은 사람이 기억해야 할 것: "이 학회는 정직하고 방법론이 탄탄하다"
- 화려함이 아니라 **신뢰**로 승부. 틀리더라도 "왜 틀렸는지" 추적할 수 있는 보고서

## 워크플로우 (v11 확정, 2026.03.28 찬희님 직접 설계)

**핵심: 엑셀이 Single Source of Truth. 보고서의 모든 숫자는 엑셀에서 온다.**

```
Phase 0: MCP 데이터 수집
  → dart_financial_statements (CFS+OFS 5개년)
  → dart_company_info, dart_major_shareholders
  → stocks_quote, stocks_history (일봉)
  → ecos_get_base_rate, ecos_get_exchange_rate
  → news_search, news_market_sentiment
  → mock 금지. 못 가져온 건 빈칸 → 찬희님 수동

Phase 1: 추가 리서치
  → DART 사업보고서 본문 정독 (섹션 30-1)
  → 기업 홈페이지 WebFetch (이미지/IR)
  → 산업별 필수 체크리스트 (섹션 30-2)
  → 지정학 리스크 스캔 (섹션 30-3)
  → 애널리스트 보고서 크로스체크

Phase 2: 엑셀 시트 v1 빌드
  → 수집한 실제 데이터 → 15시트 엑셀
  → IS/BS/CF + P×Q + Valuation + Peer + Macro + 주가
  → 이 엑셀이 이후 모든 분석의 기반 (Single Source of Truth)

Phase 3: 투자포인트 대략 잡기
  → 엑셀 데이터 기반 IP 3개 초안
  → 찬희님 확인 후 진행

Phase 4: 본문 작성 — 서브에이전트 6개 병렬
  → sections/*.py 파일 분리 구조 (섹션 29-1)
  → config.py에서 엑셀 데이터 import
  → 소제목마다 sidebar_wrap (2열 100%)
  → 단락 200~400자 균일 (SMIC 표준)
  → 시각화 15종+ 골고루

Phase 5: 엑셀 시트 v2 최종 업데이트
  → 본문에 사용된 모든 숫자·리서치 내용 추가
  → 데이터출처 시트 완비 (모든 수치의 원본 추적)
  → 보고서 도표의 모든 데이터가 엑셀에 존재하도록

Phase 6: HTML 빌드 + Evaluator 검증
  → python build_{종목명}.py
  → HARD_MIN 자동 검증
  → 브라우저 확인 → 피드백 반영

Phase 6.5: 백테스트 검증 (KIS Backtest MCP, v13.2)
  → 보고서 IP에서 매매 전략 자동 추출 (진입/이탈 조건)
  → KIS kis-backtest MCP로 전략 YAML 생성 + 1년 백테스트 실행
  → 결과(승률/수익률/최대낙폭/샤프비율) 추출
  → 보고서 리스크 섹션 또는 Appendix에 백테스트 결과 테이블 삽입

산출물 (3종):
  ① {종목명}_CUFA_보고서.html (화이트 테마, 2열 레이아웃)
  ② {종목명}_재무데이터.xlsx (15시트, 모든 데이터 완전 기록)
  ③ {종목명}_CUFA_본문.md (마크다운 원본)
```

**데이터 수집 우선순위**: Nexus MCP > pykrx/yfinance 직접 호출 > 재무데이터 Excel > 찬희님 수동 입력
**절대 금지**: mock/더미 데이터로 보고서 생성

## 1. 환경 세팅

```bash
pip install openpyxl pandas matplotlib pykrx yfinance requests lxml --break-system-packages
# DART/FRED/ECOS API 키는 환경변수에서 읽기
# DART_API_KEY, FRED_API_KEY, ECOS_API_KEY
```

## v14.1 변경 로그 (2026.04.04, 이노스페이스 ALL PASS 달성)

### Evaluator v2 — 품질 강제 시스템 완성
- **HARD_MIN**: text >= 80,000자 / svg >= 25 / tables >= 25 / h2h3 >= 20
- **SMIC_STYLE**: bold_first >= 150 / avg_para 150~450 / cross_ref >= 5 / dongsa 40~120 / transitions 30+ / counter_arg 3+ / callout 3+
- **HALLUCINATION 탐지**: "약 N%", "대략", "정도로 추정", "일반적으로", "보통", "통상적으로" → WARNING
- **SECTION_CHARS**: 섹션별 최소 글자수 (sec1:3K / sec2:10K / sec3-5:각4K / sec6:5K / sec7:3K / sec8:5K / sec9:4K / sec10:3K / sec11:2K)
- **--style-report 모드**: bold 미적용 단락 리스트업, 할루시네이션 패턴 상세 출력

### components.py 추가 컴포넌트 (v14.1)
- `chart_with_insight(chart_html, insight, src)` — 차트 + 해석 블록 (SMIC 패턴)
- `chart_pair(chart1, chart2)` — 2열 차트 배치
- `kill_condition_gauge(conditions)` — Kill Condition 신호등 시각화
- `assumption_tracker(assumptions)` — 가정 추적 테이블 (CUFA 고유 킬러 피처)

### build.py 제네릭화 (v14.1, 보안 감사)
- 이노스페이스 전용 하드코딩 텍스트 제거 → 모든 fallback 섹션이 config 기반 제네릭
- 제품 테이블 헤더: `PRODUCT_HEADERS` config 변수로 동적 결정 (로켓/반도체/금융 다 가능)
- Executive Summary 섹션 추가 (커버↔TOC 사이)
- KIS_MCP_URL 환경변수 대응

### sections.py 플러그인 — C 주입 메커니즘
```python
# build.py가 sections.py를 로드할 때:
spec = importlib.util.spec_from_file_location("custom_sections", sections_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.C = C  # 반드시 exec_module 이후에 주입! (sections.py의 C = None을 덮어씀)
```
주의: `mod.C = C`는 반드시 `exec_module` **이후**에 호출해야 함. 이전에 하면 `C = None`으로 덮어써짐.

### v14 아키텍처 (2026.04.04 초기)
- **GitHub 레포**: `pollmap/cufa-equity-report` (Public, MIT License, 7 commits)
- **HD건설기계 v4-1 CSS = 표준 확정**: `template/style.css`는 절대 수정 금지
- **build.py 자동 빌드**: `config.py → build.py → HTML 보고서` 원커맨드
- **SVG 15종 인라인**: matplotlib 제거, 순수 Python SVG 생성 (외부 의존성 0)

### 핵심 교훈 (이노스페이스 ALL PASS 세션)
1. **CSS를 매번 새로 만들지 마라** → HD건설기계 표준 CSS 복사 후 데이터만 교체
2. **클래스명 통일** → .sidebar-kw/.kw/.kw-val (HD 호환). 구 .sidebar-wrap 절대 금지
3. **build_template.py 단일 파일 = 실패** → template/ + builder/ 분리 구조
4. **인라인 SVG > matplotlib PNG** → HTML 단일 파일 배포, 외부 의존성 제거
5. **sections 플러그인** → 자동 생성 골격 + 커스텀 본문 = 최적 밀도
6. **Evaluator가 품질을 강제** → ALL PASS까지 반복 = 누구든 동일 품질 보장
7. **제네릭 fallback** → build.py에 종목별 텍스트 하드코딩 금지

### Nexus MCP 통합 (설계 완료, 구현 대기)
- `data/collector.py` → MCP 5대 도구로 config.py 자동 생성
- SSH 터널 방식 (VPS 127.0.0.1:8100 → 로컬 18100)
- 에러 시 None + TODO 주석 (빌드 중단 없음)

## 2. 프로젝트 구조 (v14.1)

### GitHub 레포 구조 (pollmap/cufa-equity-report, 7 commits)
```
cufa-equity-report/                 ← GitHub Public 레포
├── template/                       ← 표준 디자인 시스템 (수정 금지)
│   ├── style.css                   ← HD건설기계 v4-1 CSS (95줄, 확정, 수정 금지!)
│   ├── style_extended.css          ← CUFA 추가 (counter-arg, callout, chart-insight, kill-grid, float-toc)
│   ├── components.py               ← SVG 15종 + 테이블 + 레이아웃 + chart_with_insight + kill_gauge
│   └── interactive.js              ← Float TOC, 진행률 바, 접기/펼치기
├── builder/
│   ├── build.py                    ← 메인 빌드 엔진 (config → HTML, 제네릭화 완료)
│   └── evaluator.py                ← Evaluator v2 (HARD_MIN + SMIC_STYLE + HALLUCINATION + SECTION_CHARS)
├── data/
│   ├── collector.py                ← (예정) MCP 데이터 자동 수집
│   └── templates/config_template.py ← 종목별 config 템플릿
├── trading/
│   ├── strategy_extractor.py       ← IP → 매매전략 YAML
│   └── backtest_runner.py          ← KIS MCP 백테스트 연동 (KIS_MCP_URL 환경변수)
├── examples/
│   └── 이노스페이스/               ← ALL PASS 검증 완료
│       ├── config.py               ← 종목 데이터 (Single Source of Truth)
│       └── sections.py             ← 커스텀 본문 (80,002자, bold 154, cross-ref 5)
├── docs/MCP_INTEGRATION.md         ← Nexus MCP 통합 설계
├── output/                         ← 생성된 보고서 (.gitignore)
├── README.md                       ← 완전한 사용 가이드 (다른 AI 사용법 포함)
├── LICENSE (MIT)
└── .gitignore                      ← output/*.html/yaml/json, examples/**/*.html
```

### 빌드 파이프라인
```
config.py (데이터 = Single Source of Truth)
    ↓
python builder/build.py examples/{종목}/config.py
    ↓ sections.py 있으면 커스텀 본문 로드 (C 주입 메커니즘)
    ↓ 없으면 config 기반 제네릭 자동 생성 (~22K chars)
output/{종목}_CUFA_보고서.html
    ↓
python builder/evaluator.py output/{종목}_CUFA_보고서.html
    ↓ HARD_MIN + SMIC_STYLE + HALLUCINATION + SECTION_CHARS
결과: ALL PASS → 완료! / FAIL → 어디가 부족한지 정확히 진단
    ↓
python builder/evaluator.py output/{종목}_CUFA_보고서.html --style-report
    ↓ bold 미적용 단락 리스트, 할루시네이션 패턴 상세
```

### Evaluator v2 검증 기준 (v14.1 확정)
| 카테고리 | 항목 | 기준 |
|---------|------|:----:|
| HARD_MIN | text_80k | 80,000자+ |
| HARD_MIN | svg_25 | 25개+ |
| HARD_MIN | tables_25 | 25개+ |
| HARD_MIN | h2h3_20 | 20개+ |
| SMIC_STYLE | bold_first_150 | 150개+ |
| SMIC_STYLE | avg_para_len | 150~450자 |
| SMIC_STYLE | cross_ref_5 | 5개+ |
| SMIC_STYLE | dongsa_ratio | 40~120 |
| SMIC_STYLE | transitions_30 | 30개+ |
| SMIC_STYLE | counter_args_3 | 3개+ |
| SMIC_STYLE | callout_3 | 3개+ |
| HALLUCINATION | 패턴 탐지 | 0건 목표 |
| SECTION_CHARS | sec1~sec11 | 개별 기준 |

### 구 구조 (레거시, 더 이상 사용하지 않음)
```
cufa_report_{종목코드}/             ← 종목마다 별도 디렉토리 (폐기)
└── src/build_template.py          ← CSS+JS+SVG 단일 파일 (폐기)
```

## 3. config.py — 종목 설정 + 테마 + 상수

```python
import os
from dataclasses import dataclass

# === API 키 ===
DART_API_KEY = os.environ.get('DART_API_KEY', '')
FRED_API_KEY = os.environ.get('FRED_API_KEY', '')
ECOS_API_KEY = os.environ.get('ECOS_API_KEY', '')

# === 종목 설정 (파일럿마다 여기만 수정) ===
TICKER = '042670'
COMPANY_NAME = 'HD현대인프라코어'
COMPANY_NAME_EN = 'HD Hyundai Infracore'
MARKET = 'KOSPI'
SUBTITLE = '보고서 부제를 여기에'  # 예: "Shaheen-ing Oil"

PEERS_KR = {'241560': '두산밥캣'}
PEERS_GLOBAL = {'CAT': 'Caterpillar', '6301.T': 'Komatsu'}

TEAM_NAME = 'CUFA X팀'
TEAM_MEMBERS = ['이름1', '이름2', '이름3']

# === 페이지 설정 (SMIC 역공학, mm 단위) ===
@dataclass
class PageSpec:
    width_mm: float = 210
    height_mm: float = 297
    margin_top_mm: float = 20
    margin_bottom_mm: float = 15
    margin_left_mm: float = 18
    margin_right_mm: float = 18
    header_height_mm: float = 12
    footer_height_mm: float = 10

    @property
    def content_width_mm(self):
        return self.width_mm - self.margin_left_mm - self.margin_right_mm

PAGE = PageSpec()

# === SMIC 2단 레이아웃 비율 ===
SIDEBAR_RATIO = 0.20   # 좌측 사이드노트 20%
BODY_RATIO = 0.78      # 우측 본문 78%
GAP_RATIO = 0.02       # 간격 2%

# === 폰트 사양 (SMIC 역공학) ===
@dataclass
class FontSpec:
    family: str
    size_pt: float
    bold: bool = False
    color_hex: str = '333333'
    line_spacing: float = 1.5

FONTS = {
    'page_header':     FontSpec('맑은 고딕', 8,    False, '666666', 1.0),
    'section_title':   FontSpec('맑은 고딕', 16,   True,  '000000', 1.3),
    'section_subtitle':FontSpec('맑은 고딕', 13,   True,  '000000', 1.3),
    'subsection':      FontSpec('맑은 고딕', 10,   True,  '000000', 1.3),
    'sidebar':         FontSpec('맑은 고딕', 8.5,  True,  '333333', 1.3),
    'body':            FontSpec('맑은 고딕', 9,    False, '333333', 1.5),
    'body_bold':       FontSpec('맑은 고딕', 9,    True,  '000000', 1.5),
    'chart_title':     FontSpec('맑은 고딕', 8,    True,  '000000', 1.0),
    'chart_unit':      FontSpec('맑은 고딕', 7,    False, '999999', 1.0),
    'chart_source':    FontSpec('맑은 고딕', 7,    False, '999999', 1.0),
    'table_header':    FontSpec('맑은 고딕', 8,    True,  'FFFFFF', 1.0),
    'table_data':      FontSpec('맑은 고딕', 8,    False, '333333', 1.0),
    'page_number':     FontSpec('맑은 고딕', 8,    False, '666666', 1.0),
}

# === 재무 테이블 색상 ===
TABLE_COLORS = {
    'header_bg': '333333',
    'header_text': 'FFFFFF',
    'row_even': 'F5F5F5',
    'row_odd': 'FFFFFF',
    'border': 'CCCCCC',
    'negative': 'E63946',
}

# === matplotlib 차트 테마 ===
CHART_LIGHT = {
    'bg': '#FFFFFF',
    'text': '#333333',
    'grid': '#E8E8E8',
    'spine': '#CCCCCC',
    'primary': '#7c6af7',       # 시그니처 퍼플 — 동사
    'secondary': '#4A7FB5',     # 블루 — Peer/비교
    'tertiary': '#2A9D8F',      # 틸 — 보조
    'quaternary': '#F4A261',    # 앰버 — 4번째
    'gray': '#CCCCCC',
    'positive': '#2A9D8F',
    'negative': '#E63946',
}

CHART_DARK = {
    'bg': '#0a0a0a',
    'text': '#e0e0e0',
    'grid': '#1a1a1a',
    'spine': '#333333',
    'primary': '#a78bfa',       # 밝은 퍼플
    'secondary': '#6CB4EE',
    'tertiary': '#4ECDC4',
    'quaternary': '#FFD93D',
    'gray': '#333333',
    'positive': '#4ECDC4',
    'negative': '#FF6B6B',
}

# === HTML 인터랙티브 CSS 변수 ===
HTML_THEME = {
    'bg': '#0a0a0a',
    'surface': '#0f0f0f',
    'surface2': '#141414',
    'border': '#222222',
    'text': '#e0e0e0',
    'text2': '#888888',
    'text3': '#555555',
    'purple': '#7c6af7',
    'purple_light': '#a78bfa',
    'purple_bg': '#12101f',
    'purple_border': '#2d2654',
    'positive': '#4ecdc4',
    'negative': '#ff6b6b',
    'blue': '#6cb4ee',
    'amber': '#ffd93d',
}

# === 도표 번호 체계 ===
# 도표 X-Y. (X=섹션번호, Y=섹션 내 순번)
# 1:산업분석 2:기업분석 3:TP① 4:TP② 5:Plus α 6:매출추정 7:비용추정 8:밸류에이션

# === 서술 규칙 ===
# - 소제목마다 첫 문장 Bold로 주장 선언 → 보통체로 근거 전개
# - 밑줄은 결론 1~2문장에만
# - 단정적 서술체: "~이다" (○), "~할 것으로 판단된다" (×)
# - 경어 미사용
# - 출처 없는 주장 0개 목표: 모든 수치/팩트에 "(출처: XXX)" 필수
# - 정성 평가 금지: "좋다/나쁘다" 대신 숫자로 근거 제시

# === SMIC 문체 규칙 (v12 신규 — 모든 본문에 적용) ===
#
# ▸ '동사' 지칭 원칙
#   분석 대상 기업을 **'동사'**로 호칭한다 (SMIC 4편 평균 108회/편).
#   ✅ "동사는 TC2C 공정이 완성될 경우 약 70%의 전환율을 달성할 것임을 제시했다."
#   ✅ "동사의 배당은 이익과 투자에 의해 결정된다."
#   ✅ "동사는 현재 25개국 이상에서 리쥬란 3종에 대해 품목허가를 획득했다."
#   ❌ "JYP는~", "KSS해운은~" → 기업명 직접 사용 금지 (커버/기업개요 첫 등장 1회만 예외)
#
# ▸ '본서는/에서는' 사용
#   보고서 자체가 주장·판단·전망할 때 사용한다.
#   - "본서는 26년까지 유가가 두바이유 기준 $60/배럴 선에서 지지될 것으로 전망한다."
#   - "본서에서는 이러한 조정이 심리적 요인에 기인한 일시적 현상으로 판단한다."
#   - "본서는 동사의 Valuation 방법으로 PBR Method를 선택하였다."
#
# ▸ '전술한/후술할' 크로스레퍼런스
#   섹션 간 논리를 연결한다 (SMIC S-Oil 14회 사용). 보고서의 유기적 흐름 핵심.
#   - "전술한 바와 같이 미국, 중국의 가파른 증설로 가동률이 하락하고~"
#   - "[투자포인트 1]에서 전술한 것처럼 원가 우위를 바탕으로~"
#   - "[5. 투자포인트 2]에서 후술하겠지만 미국 내 시추리그 수가 감소하고 있다는 점과~"
#   - "전술했듯이 윤활부문은 안정적이고 높은 마진으로 정유와 석화의 변동성을 완화해준다."
#
# ▸ 볼드-첫문장 원칙 (SMIC 핵심 패턴, 4편 평균 338개/편)
#   **모든 단락의 첫 문장은 핵심 주장을 볼드 처리한다.**
#   단락 구조: 볼드 1문장(핵심 주장, 20~40자) + 일반 3~5문장(근거 전개, 150~300자)
#   HTML: <strong>첫 문장.</strong> 나머지 문장들.
#   SMIC 원문 예시:
#   - "**정유사는 저질의 정제유를 고품질의 경질유로 바꾸기 위해 고도화 설비 도입을 늘리고 있다.** 고도화 설비란~"
#   - "**스킨부스터는 글로벌 에스테틱 시장에서 가장 빠르게 성장하는 카테고리다.** 스킨부스터는 유효성분을~"
#   - "**리쥬란은 여전히 건재하다.** 9,10월 리쥬란에 대한 구글 트렌드는~"
#   - "**ECM도 리쥬란을 막을 수 없다.** ECM 기반의 스킨부스터는~"
#
# ▸ 전환 패턴 7종 (단락 간 연결)
#   | 패턴               | 용도         | 원문 예시 |
#   |--------------------|-------------|----------|
#   | "전술한 바와 같이~"  | 이전 섹션 연결 | "전술했듯이 윤활부문은 안정적이고 높은 마진으로~" |
#   | "그렇다면~"          | 질문→답변    | "그렇다면 유가가 $60/배럴에서 지지될 수 있는 근거를 알아보자." |
#   | "이에 더해~"         | 추가 논점    | "이에 더해 과거에는 찌꺼기로 여겨진 저질유까지도~" |
#   | "한편~"              | 시각 전환    | "한편 국내 석화사들은 NCC 감축을 추진 중이다." |
#   | "이처럼~"            | 소결        | "이처럼 동사의 마진 구조는 구조적으로 개선되고 있다." |
#   | "실제로~"            | 사례 제시    | "실제로 2015년 사이클에서도 유사한 패턴이 관찰되었다." |
#   | "다만~"              | 리스크 인정  | "다만 15년과 현재가 유사한 국면만 가지고 있는 것은 아니다." |
#
# ▸ 원문자(①②③) 사용 — 복수 논점 나열 시 필수
#   "본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다.
#    ① 공정 구조의 차이 ② 글로벌 공급 과잉 압력 완화 ③ 아람코의 전략적 의도"
#
# ▸ 전망형 종결어미
#   ~것으로 판단한다 / ~전망이다 / ~것이다 / ~예정이다

# === 사이드바 노트 규칙 (v9, SMIC 벤치마크) ===
# SMIC 보고서의 핵심 차별점: 모든 페이지 우측에 "해석적 한줄" 사이드 노트
# - 밀도: 문단당 1~2개 (섹션 시작부만 X → 모든 문단에!)
# - 내용: 숫자 키워드가 아닌 "해석적 한줄"
#   ○ "전환사채에 대한 과도한 우려" (해석)
#   ○ "OTT와 만난 서브컬처" (관점)
#   ○ "주주환원의 낌새" (전망)
#   × "합병출범 2026.01" (단순 숫자)
#   × "매출 2.3조" (단순 숫자)
# - 역할: 스캔 리딩 시 사이드바만 읽어도 전체 논지 파악 가능
#
# ▸ 사이드바 키워드 유형 4종 (v12, SMIC 표준)
#   | 유형         | 예시                              | 용도     |
#   |-------------|----------------------------------|----------|
#   | 소제목형     | "정유-화학 산업이란?"              | 주제 전환 |
#   | 포인트 요약형 | "수율 대폭 개선 :COTC"            | 핵심 결론 |
#   | 키워드 강조형 | "마진(1): 스프레드"               | 개념 분류 |
#   | 주의 표시형   | "⚠ 아직 생산능력으로 집계되지 않음" | 경고/주의 |
#   - 길이: 3~15자 (한글 기준). 15자 초과 시 2줄로 분할
#   - 동일 주제 2건+: 번호 부여 ("한국 구조조정 1)", "한국 구조조정 2)")
#   - 콜론 구분: "수익성 제고 : 수율 개선" (상위 주제→하위 포인트)

# === 추론 깊이 규칙 (v9, SMIC 벤치마크) ===
# 모든 투자포인트는 최소 4단계 추론 체인 필수
# 2~3단계 (CUFA 현재):
#   산업 성장 → 매출 증가 → 주가 상승 (부족)
# 4~5단계 (SMIC 수준, 목표):
#   트렌드 → 구조적 변화 → 기업 포지셔닝 → 수익 영향 → 밸류에이션 리레이팅
# 예시 (SMIC 파마리서치):
#   비침습 트렌드 → 스킨부스터 시장 확대 → PN 원천기술 독점 → 공급 제약 → ASP 상승 유지
# 예시 (SMIC 애니플러스):
#   코로나→OTT 확산 → 오타쿠 소비문화 주류화 → 일본 콘텐츠 수요 폭증 → 밸류체인 독점 이점

# === 투자포인트 내 반박 통합 (v9) ===
# SMIC 패턴: 투자포인트 본문 안에서 "시장의 우려 → 데이터 반박 → 결론" 3단 논증
# 별도 리스크 섹션은 유지하되, 투자포인트 내에서도 반박을 통합
# counter_arg 최소 3건: IP마다 1건 + 추가 반박 필수
# 파마리서치 예시: ECM 위협에 대해 10페이지 분량 반박 (임상논문 편수, Bibliometric 분석, 규제 비교)
#
# ▸ 리스크 반박 2중 구조 (v12, SMIC + CUFA 융합)
#   인라인 반박 (본문 내, SMIC 스타일):
#     본문 흐름 안에서 리스크 제기 → "다만/그러나" → 정량 반박 → "따라서~"
#     IP당 최소 1건
#     원문: "그렇다면 동사의 설비 증설이 정부의 사업재편 기조와 충돌할 위험은 없는 것일까?
#            본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다."
#   counter_arg 블록 (별도 UI, CUFA 스타일):
#     독립 박스로 "시장의 우려" vs "반박" 대립 구조. IP당 최소 1건.
#   양쪽 결합: IP당 인라인 반박 1건 + counter_arg 블록 1건 = 최소 2건

# === 독자적 데이터 (v9, SMIC 최대 차별점) ===
# IR/DART 데이터 정리만으로는 SMIC을 넘지 못한다
# SMIC 파마리서치가 S등급인 핵심 이유:
#   - 의료인 9명 직접 인터뷰
#   - 강남언니 앱에서 시술가격 100건+ 수집
#   - 뷰티카페 게시글 1,394건 카운트
#   - 건강보험 피보험자수 추적
# Nexus MCP로 대체 가능한 독자적 데이터:
#   - news_keyword_volume: 키워드 트렌드 (네이버)
#   - news_trend: 뉴스 트렌드 분석
#   - academic_semantic_scholar: 학술논문 (Bibliometric)
#   - patent_search: 특허 동향
#   - gdelt_search: 글로벌 뉴스 감성
# 사람이 해야 하는 독자적 데이터:
#   - 업계 관계자 인터뷰
#   - 앱/커뮤니티 직접 크롤링 (집계/통계만, 개인정보 금지)
#   - 현장 방문/탐방

# === 애널리스트 보고서 크로스체크 (v9, 필수) ===
# 보고서 작성 전 반드시 해당 종목의 증권사 애널리스트 보고서를 확인한다.
# 확인 소스:
#   - 한경 컨센서스 (consensus.hankyung.com)
#   - 네이버 증권 리서치 (finance.naver.com → 종목분석 → 리서치)
#   - FnGuide 컨센서스
#   - 증권사 리서치센터 직접 (미래에셋, 키움, 신한 등)
#
# 확인 항목:
#   - 컨센서스 목표주가 (평균/최고/최저)
#   - 컨센서스 EPS/매출/영업이익 추정치
#   - 최근 3개월 투자의견 변경 내역
#   - 애널리스트가 주목하는 핵심 이슈/카탈리스트
#   - 우리 추정치와 컨센서스 괴리 확인 → 괴리 사유 서술 필수
#
# ★★★ 절대 규칙: 다른 보고서 내용 복사/인용 금지 ★★★
#   - 애널리스트 보고서는 "참고"만 가능
#   - 우리의 투자의견, 추정치, 목표주가는 100% 독자적 분석으로 도출
#   - 다른 보고서의 논리/문장/표현을 가져오면 안 됨
#   - 컨센서스 수치 인용 시: "컨센서스 평균 OPM 15.2% (출처: FnGuide)" 형태로만
#   - "~증권은 ~라고 분석했다" 식의 인용도 금지 → 우리 자체 분석만
#
# 컨센서스 대비 우리 추정치 괴리 서술 (Valuation 섹션 필수):
#   "CUFA 추정 EPS 62,000원은 컨센서스 평균 58,500원 대비 +6.0% 높다.
#    이는 당사가 BPR(불닭침투율) 기반 독자 추정 모델을 적용하여
#    중국/유럽 매출 성장률을 컨센서스 대비 보수적으로 산정한 결과이다."

# === 추정 가정 근거 표준 (v9) ===
# 모든 P×Q 가정에 "왜 이 수치인지" 1~2문장 근거 필수
# × "ASP 1.8억원, 출하 18,683대" (근거 없음)
# ○ "ASP 1.8억원 (2025A 1.7억 대비 +5.9%, 고사양 HX시리즈 믹스 개선 반영, 출처: IR 자료 p.23)"
```

## 4. (삭제됨 — v13에서 DOCX 출력 제거. HTML 전용 빌드로 전환)


## 5. chart_factory.py — matplotlib 차트 생성

```python
"""
CUFA 표준 차트 생성기.
모든 차트를 라이트 + 다크 2벌 생성.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.dates import DateFormatter
import numpy as np
from config import CHART_LIGHT, CHART_DARK

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

def _setup(theme_dict, figsize=(6, 4)):
    """공통 차트 설정"""
    t = theme_dict
    fig, ax = plt.subplots(figsize=figsize, facecolor=t['bg'])
    ax.set_facecolor(t['bg'])
    ax.tick_params(colors=t['text'], labelsize=8)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    for s in ['left', 'bottom']:
        ax.spines[s].set_color(t['spine'])
        ax.spines[s].set_linewidth(0.5)
    ax.grid(True, color=t['grid'], linewidth=0.5, alpha=0.7)
    ax.xaxis.label.set_color(t['text'])
    ax.yaxis.label.set_color(t['text'])
    ax.title.set_color(t['text'])
    return fig, ax, t

def _save(fig, path, dpi=250):
    fig.tight_layout(pad=1.5)
    fig.savefig(path, dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

def _add_source(ax, text, t):
    ax.annotate(f'출처: {text}', xy=(0, -0.13), xycoords='axes fraction',
                fontsize=7, color=t.get('gray', '#999999'), ha='left')

def create_chart_both(name, draw_func, *args, **kwargs):
    """
    라이트+다크 2벌 동시 생성.
    draw_func(fig, ax, t, *args, **kwargs)를 호출.
    """
    for theme_name, theme_dict, folder in [
        ('light', CHART_LIGHT, 'charts'),
        ('dark', CHART_DARK, 'charts_dark'),
    ]:
        fig, ax, t = _setup(theme_dict, figsize=kwargs.get('figsize', (6, 4)))
        draw_func(fig, ax, t, *args, **kwargs)
        _save(fig, f'{folder}/{name}.png')

# === 예시 차트 함수들 ===

def draw_price_12m(fig, ax, t, dates, prices, current_price, change_pct, **kw):
    """표지용 12M 주가 차트"""
    ax.plot(dates, prices, color=t['primary'], linewidth=1.5)
    ax.fill_between(dates, prices, alpha=0.1, color=t['primary'])
    ax.set_title('')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    # 현재가 표시
    ax.annotate(f'₩{current_price:,} ({change_pct:+.1f}%)',
                xy=(dates[-1], prices[-1]),
                fontsize=9, color=t['primary'], fontweight='bold',
                ha='right')
    _add_source(ax, 'pykrx, CUFA', t)

def draw_revenue_opm(fig, ax, t, years, revenue, opm, **kw):
    """매출액 + OPM 이중축 차트"""
    ax2 = ax.twinx()
    ax.bar(years, revenue, color=t['primary'], alpha=0.7, width=0.6, label='매출액')
    ax2.plot(years, opm, color=t['negative'], marker='o', markersize=4, label='OPM(%)')
    ax.set_ylabel('매출액 (십억 원)', fontsize=8, color=t['text'])
    ax2.set_ylabel('OPM (%)', fontsize=8, color=t['text'])
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(t['spine'])
    ax2.tick_params(colors=t['text'], labelsize=8)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.1f}%'))
    _add_source(ax, 'DART, CUFA', t)

def draw_pbr_band(fig, ax, t, dates, prices, bps_series, multiples, **kw):
    """Historical PBR 밴드"""
    colors = [t['gray'], t['tertiary'], t['secondary'], t['primary'], t['negative']]
    for i, m in enumerate(multiples):
        band = [bps * m for bps in bps_series]
        ax.plot(dates, band, color=colors[i % len(colors)],
                linewidth=0.8, linestyle='--', alpha=0.6)
        ax.annotate(f'{m:.1f}x', xy=(dates[-1], band[-1]),
                    fontsize=7, color=colors[i % len(colors)])
    ax.plot(dates, prices, color=t['primary'], linewidth=1.5, label='주가')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    _add_source(ax, 'pykrx, DART, CUFA', t)
```

## 6. HTML 디자인 금지 사항 (반드시 준수)

- 귀여운 느낌 절대 금지
- box-shadow 과용 금지
- 과한 글로우/그라데이션 금지
- 모바일앱식 과장 애니메이션 금지
- 데이터 밀도를 떨어뜨리는 여백 남용 금지
- border-radius 최대 4px (둥글둥글 금지)
- 외부 CDN/라이브러리 일체 금지 (순수 HTML/CSS/JS만) — **예외: Google Fonts @import는 허용** (Noto Sans KR 로드 필수)

## 7. 찬희님 선호 (최우선 준수)

- **목업 데이터 절대 금지** — API에서 못 가져온 데이터는 빈칸으로
- **시그니처 퍼플**: #7c6af7 (메인) ~ #a78bfa (밝은)
- **다크 배경**: #0a0a0a base / #0f0f0f surface
- **SMIC 레이아웃 100% 복제**: 좌측 사이드노트 + 우측 본문 + 하단 차트 2개 병렬
- **모든 페이지 꽉 차게** — 여백 남용 = 실패
- **단정적 서술체**: "~이다" (○)
- **Bold 도입문 + 밑줄 결론문** 패턴 엄수
- **한국어 100%**
- **정성 평가 금지** — 모든 분석은 정량 데이터 기반. "좋다/나쁘다" 대신 숫자로 근거 제시
- **최신 날짜 자동 기준 (KST 필수)**:
  - 보고서 작성일: 한국시간(KST, UTC+9) 기준 `datetime.now(ZoneInfo('Asia/Seoul'))`
  - 주가 데이터: 작성일 기준 최근 거래일 종가
  - 재무제표: 최신 공시 기준 (분기/연간 자동 판별)
  - 매크로 데이터: MCP 호출 시 최신 데이터 자동 수집
  - 뉴스/이슈: 작성일 기준 최근 3개월 이내만 인용
  - 환율/금리: 작성일 기준 당일 또는 전일 종가
  - 표지/헤더에 "작성일: 2026년 X월 X일 (KST)" 자동 삽입
  - **Evaluator 자동 검증**: 보고서 내 모든 날짜가 작성일 ±6개월 이내인지 체크. 1년 이상 된 데이터는 경고

```python
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')
REPORT_DATE = datetime.now(KST)
REPORT_DATE_STR = REPORT_DATE.strftime('%Y년 %m월 %d일')
REPORT_YEAR = REPORT_DATE.year
# 추정 연도: 올해(E), 내년(E), 내후년(E)
EST_YEARS = [REPORT_YEAR, REPORT_YEAR + 1, REPORT_YEAR + 2]
# 실적 연도: 올해-1(A), 올해-2(A), 올해-3(A)
ACTUAL_YEARS = [REPORT_YEAR - 1, REPORT_YEAR - 2, REPORT_YEAR - 3]
```

**⚠ v12 CRITICAL: 날짜 하드코딩 절대 금지**
- config.py에서 `REPORT_DATE = datetime.now(KST)` 필수. `'2026-03-28'` 등 문자열 하드코딩 금지.
- MCP 데이터 수집 시 "가장 최근 거래일" 자동 탐색: `stocks_history`에서 오늘~7일 전 범위로 조회, 가장 마지막 데이터 사용.
- `stocks_quote`는 장중이면 실시간, 장 마감이면 전일 종가 → 반드시 시점 확인.
- Phase 0에서 수집한 데이터의 기준일을 config.py 상단에 `DATA_AS_OF = '2026-03-28'` 형태로 명시 (자동 생성).
- **서브에이전트에게도 전달**: "오늘 날짜는 {REPORT_DATE_STR}이다. 이 날짜 기준 최신 데이터를 사용하라."

## 8. 89점+ 자동 달성 빌드 시스템 (v8 아키텍처)

### 8-0. 핵심 원칙: Markdown-First 워크플로우

**현대건설 v1의 교훈**: Python에서 직접 HTML을 쓰면 텍스트가 항상 부족해진다.
**해결**: 마크다운으로 먼저 75,000자+ 본문을 작성 → 검증 → HTML 변환.

```
Phase 0: Nexus MCP 데이터 수집 (기본) or 재무데이터 Excel
  → dart_financial_statements: IS/BS/CF 5개년 (CFS 연결 필수!)
  → stocks_market_overview / pykrx: 주가, PER/PBR 밴드
  → ecos_search: 금리, 환율, GDP 등 매크로 변수
  → MCP 실패 시 pykrx/yfinance 직접 호출, 그래도 안 되면 찬희님 수동
  → {종목명}_재무데이터.xlsx 있으면 읽어서 Appendix 자동 생성
  ↓
Phase 1: 마크다운 본문 작성 (60,000자+ 필수, 75,000자+ 우수)
  → {종목명}_CUFA_본문.md (순수 텍스트+테이블)
  → 섹션별 최소 자수 검증
  ↓
Phase 2: HTML 변환 (build_template.py 기반)
  → 마크다운 본문을 sidebar_wrap()에 삽입
  → SVG 차트/다이어그램 추가
  → 인터랙티브 요소(expand_card, counter_arg, scenario_tabs) 삽입
  → 스크롤 UX(progress, float-toc, dots, page-break) 적용
  ↓
Phase 3: Evaluator 검증 (자동)
  → 89점 체크리스트 전항목 검증
  → 미달 시 자동 보강 → 재검증
  ↓
Output (전체 산출물 — 빌드 완료 시 자동 생성):
  → {종목명}_CUFA_보고서.html      (인터랙티브 HTML, 250KB+, 75K자+, SVG 50+, 테이블 25+)
  → {종목명}_CUFA_본문.md           (마크다운 원본, 60K자+, Phase 1 산출물)
  → {종목명}_재무데이터.xlsx        (15시트: CFS 6 + OFS 5 + 공통 4 — 모든 수치 출처 추적 가능)
  → (v13에서 DOCX 제거, HTML 전용)
  → build_{종목명}.py               (빌드 스크립트, build_template.py 기반)
  → data/                           (수집 원본 데이터 — CSV, JSON, MCP 응답)
  → charts/ + charts_dark/          (matplotlib 차트 PNG, 라이트+다크 2벌)

  **디렉토리 구조 (최종)**:
  ```
  cufa_report_{종목코드}/
  ├── build_{종목명}.py          # 빌드 스크립트
  ├── data/
  │   ├── {종목명}_CUFA_본문.md  # 마크다운 원본 (Phase 1)
  │   ├── financials.xlsx        # MCP 수집 원본
  │   ├── stock_price.csv        # 주가 데이터
  │   └── 1차데이터/             # 크롤링/인터뷰 원본
  ├── output/
  │   ├── {종목명}_CUFA_보고서.html
  │   ├── {종목명}_CUFA_보고서.html
  │   └── {종목명}_재무데이터.xlsx
  ├── charts/                    # 보고서 차트 리소스
  └── charts_dark/               # 다크 테마 (HTML용)
  ```

  **산출물 검증 (build 완료 시 자동 체크)**:
  - [ ] HTML 존재 + HARD_MIN 통과
  - [ ] 마크다운 원본 존재 (60K자+)
  - [ ] 엑셀 15시트 존재 + 데이터출처 시트 완비
  - [ ] 1차 데이터 원본 보존 (크롤링 CSV, 인터뷰 메모 등)
```

### 8-0a. 마크다운 본문 작성 가이드 (Phase 1)

**"SMIC S-Oil 보고서 하나만으로 아무것도 모르는 사람도 이해할 수 있다"**
이것이 우리가 지향하는 수준이다. 모든 보고서는 다음을 충족해야 한다:

#### 섹션별 마크다운 최소 요구사항

```
## 표지 (Cover, SMIC 형식 100% 카피)

SMIC 표지 구조를 그대로 따른다:

```
┌─────────────────────────────────────────┐
│ Equity Research Report                   │
│ 종목명 (종목코드)                         │
│                                          │
│ "캐치프레이즈" ← 보고서 핵심 메시지 1문장  │
│                                          │
│ 투자의견: BUY   목표주가: XX,XXX원         │
│ 현재가: XX,XXX원  업사이드: +XX.X%         │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ 핵심 투자포인트 (Main Idea)          │ │
│ │                                      │ │
│ │ ① 투자포인트 제목 ──→ 근거 요약 1줄   │ │
│ │ ② 투자포인트 제목 ──→ 근거 요약 1줄   │ │
│ │ ③ 투자포인트 제목 ──→ 근거 요약 1줄   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────┐  Key Financials (테이블) │
│ │ 12M 주가차트  │  매출  OPM  EPS  PER    │
│ │ (SVG 미니)   │  2024A 2025E 2026E 2027E │
│ └──────────────┘                          │
│                                          │
│ CUFA X팀 | 팀원 이름 | 작성일 2026.XX.XX  │
└─────────────────────────────────────────┘
```

**용어 변경: "IP" → "투자포인트"**
- 기존 "투자포인트①" → "투자포인트①"
- 이유: "Investment Point"는 업계 용어이나, "투자포인트"가 한국어 보고서에서 더 자연스럽고 SMIC도 "투자포인트"를 사용

## 표지 Executive Summary 강화 (v9, 글로벌 IB 패턴) — 필수
- Cover 자체가 **standalone 1-page summary**여야 함 — 바쁜 독자가 표지만 읽어도 판단 가능
- 표지 하단에 추가: (1) 투자논지 3줄 요약 (2) Risk/Reward 비율 (3) Key Debates 1줄 요약 (Bull vs Bear) (4) Conviction Level 뱃지 (5) 향후 핵심 Catalyst 3개
- **ESG 정량 통합 (v9, CFA 패턴)** — 선택 (EPS에 직접 영향 있을 때만)
  - "ESG 일반론 금지" 원칙 유지. 정량적 영향이 있는 경우에만 표지/밸류에 반영
  - 탄소 배출 비용이 COGS에 미치는 영향 (배출권 가격 × 배출량)
  - 지배구조 리스크가 Korea Discount에 미치는 영향
  - "ESG가 EPS에 ±X원 영향" 형태로만 — 정성적 ESG 점수 나열은 여전히 금지

## 0. Investment Thesis Dashboard (표지 직후, v9 Pershing Square 패턴) — 필수
- 기존 Main Idea 구조도를 **6-Box Grid**로 업그레이드:
  ```
  ┌─────────────┬─────────────┬─────────────┐
  │ THESIS      │ VARIANT     │ VALUATION   │
  │ 투자논지 3줄 │ 컨센서스 괴리│ 현재가 vs TP │
  ├─────────────┼─────────────┼─────────────┤
  │ CATALYSTS   │ RISK/REWARD │ KILL COND.  │
  │ 향후 3이벤트 │ 비율 + 확률 │ 사망조건 3개 │
  └─────────────┴─────────────┴─────────────┘
  ```
- 각 박스 클릭 시 해당 섹션으로 스크롤 (인터랙티브 HTML)
- 투자포인트 3개를 화살표로 연결: ①→②→③→목표주가
- 핵심 수치 4개 하이라이트 (매출/OPM/EPS/TP)

## 0-1. 주가분석 (3,000자+, Main Idea 직후)
- 상장 이후 (또는 최근 3~5년) 주가를 5~6개 구간으로 분할
- 각 구간별: 기간, 수익률, 핵심 이벤트, 주가 변동 원인
- SVG 차트: 주가 라인 + 구간별 색상 배경 + 이벤트 어노테이션
- "현재 주가는 어느 구간에 있는가?" → 투자 타이밍 논거 연결
- 예시 (SMIC 파마리서치):
  구간1(+45%): 신약 임상 호재 → 구간2(-22%): 금리 인상 + 공매도
  → 구간3(+30%): 해외 매출 서프라이즈 → 구간4(횡보): 카탈리스트 대기

## 0-2. Key Debates — Bull vs Bear (v9, 글로벌 IB 패턴)
- **표지 직후, 주가분석 직후에 배치** — 바쁜 독자가 이것만 읽어도 양쪽 논쟁 파악
- 좌우 2칼럼 레이아웃: **Bull 3건 vs Bear 3건 대칭 배치**
- 각 항목에: (1) 핵심 논거 1문장 (2) 확률(%) (3) EPS 영향(원) (4) 해당 섹션 앵커 링크
- **Risk/Reward Ratio** 표시: `(Bull TP - 현재가) / (현재가 - Bear TP)` → 비율 > 2.0이면 비대칭 업사이드
- 기존 counter_arg(IP 내 반박)와 역할 분리: Key Debates = "요약형 양쪽 비교", counter_arg = "상세 논파형"
- SVG 또는 HTML 그리드로 구현, 인터랙티브 HTML에서 클릭 시 해당 섹션 이동

## 0-3. Variant Perception — 컨센서스 vs CUFA (v9, 헤지펀드 패턴)
- **"시장이 X라고 보는데 우리는 Y라고 본다. 이유는 Z"** 구조
- 테이블 형태:
  ```
  | 항목 | 컨센서스 | CUFA 추정 | 괴리(%) | CUFA가 다르게 보는 이유 | 반증 조건 |
  | 매출 | 1.2조    | 1.35조   | +12.5%  | BPR 침투율 모델       | BPR < 15%면 컨센서스가 맞음 |
  ```
- **모든 괴리 항목에 반증 조건 필수** — "이 조건이 발생하면 우리가 틀린 거"
- 섹션 8(실적추정)과 연결: Variant Perception의 각 괴리 → 실적추정에서 상세 근거 전개

## 1. 기업개요 (3,000자, 압축)
- 이 기업이 뭘 하는 회사인지 3문장 요약
- 사업부별 매출 비중 + 핵심 제품 1줄씩 (테이블 1개)
- 대주주/지배구조 (테이블 1개)
- 핵심 경쟁력(해자) 3가지 — 각 1~2문장만. 근거는 이후 섹션에서
- **금지**: 뻔한 연혁 나열, ESG 일반론, CEO 이력 장황하게, "글로벌 리딩 기업" 같은 수식어
- **원칙**: 기업개요는 "명함" 수준. 투자자가 3분 안에 읽고 "아 이런 회사구나" 파악 끝

## 2. 산업분석 (10,000자+)
- **이 섹션이 보고서의 기반. 기초부터 전문적 내용까지 전부 담아야 한다.**
- **유기적 수렴 원칙 (SMIC 핵심 패턴)**:
  - 산업분석의 모든 내용이 → 기업분석으로 → 투자포인트로 → 밸류에이션으로 하나의 논리 체인으로 수렴
  - 산업분석에서 다룬 트렌드가 기업분석의 경쟁력 근거가 되고, 그 경쟁력이 투자포인트의 테제가 되고, 그 테제가 매출 추정의 가정이 되고, 그 가정이 밸류에이션의 입력값이 된다
  - **산업분석에서 언급했는데 이후 섹션에서 안 쓰이는 내용 = 삭제 대상**
  - **투자포인트에서 갑자기 나오는데 산업분석에서 근거가 없는 내용 = 논리 누락**
- 산업 기초: 시장 규모(TAM/SAM/SOM), 성장률, 구조, 수요 동인 (4,000자+)
  - "이 산업을 처음 접하는 사람도 이해할 수 있도록" — 기초부터
  - 수요-공급 구조, 가격 결정 메커니즘, 진입 장벽 — 구조적으로
  - 밸류체인 각 단계 설명 (원재료→생산→유통→최종소비자) — 전문적으로
  - Value Chain 다이어그램 SVG (SMIC JTC 패턴: 산업분석 첫 장에 배치, 기업 위치 표시)
  - 비전공자를 위한 비유 3개+ 포함
- 사이클 분석: 현재 위치, 과거 사이클 비교 (1,000자+)
- 지역별 시장: 주요 지역 3~5개 각 500자+
- 경쟁 구도: TOP 10 기업, 점유율, 포지셔닝 (1,000자+)
- 메가트렌드: 전동화/디지털화/ESG 등 (500자+)
#
# ▸ 산업분석 교육적 깊이 (v12, SMIC S-Oil 89점 기준)
#   "이 산업을 처음 접하는 사람도 완벽히 이해 가능"한 수준을 목표로 한다.
#   필수 포함 항목:
#   1. 산업 정의 & 밸류체인: 각 단계별 마진율/TOP3 플레이어 명시
#      S-Oil: Up/Mid/Downstream → 원유 분류(WTI/Brent/Dubai) → 고도화 설비
#   2. 마진 구조 설명: 해당 산업의 수익 메커니즘을 구조적으로 서술
#      정유: 스프레드/래깅효과/재고자산평가손실 3요소
#      반도체: ASP/BOM/Yield/가동률
#      해운: 운임-연료비 스프레드, T/C vs Spot
#      엔터: 음반 마진 vs 공연 마진 vs MD/IP 마진
#   3. 국가별 글로벌 비교 필수: 미국/중국/유럽/일본 각각 2~3단락 (각 800자+)
#      각국 시장 규모/규제/경쟁사/성장률/정책 방향
#      S-Oil: 미국 셰일 BEP → 사우디 비전2030 → 중국 Teapot → 유럽 구조조정
#   4. 구조조정/경쟁 구도: 산업 내 구조변화 현황 + 동사 포지션
#   5. 사이클 분석: 해당 산업의 과거 사이클(4~12년 주기) + 현재 위치

## 2-1. 기업분석 (8,000자+, 산업분석과 분리)
- 사업부별 상세 (사업부당 1,500자+): 매출 비중, 주요 제품, 경쟁사, 핵심 KPI
- 기술적 해자 / 경쟁 우위 (데이터 기반, 정성 금지)
- 경영진 전략 방향 (최근 IR/공시 기반)
- 밸류체인에서의 포지션 (산업분석 Value Chain SVG와 연결)
- 최근 주요 이벤트 (합병/인수/신사업/구조조정)
- **Management & Capital Allocation Scorecard (v9, GS SUSTAIN 패턴)** — 권장
  - 테이블 5항목 각 1~5점: (1) ROIC 5년 추세 (2) 자본배분 효율(배당/자사주/M&A/설비투자) (3) 대주주 보유지분 변동 (4) 과거 가이던스 vs 실적 괴리(서프라이즈 이력) (5) IR 투명성
  - 각 항목에 점수 + 근거 1줄. "경영진을 믿을 수 있는가"를 데이터로 판단
  - 적용 조건: 상장 3년+ 기업. 신규상장은 데이터 부족으로 생략 가능

## 3. 투자포인트① (5,000자+)
- 테제 선언 (Bold 1문장)
- 근거 3~5개 (각 600자+, 데이터와 논리로 뒷받침)
- Bear case 선제 논파 (counter_arg): "시장의 우려 → 반박" (500자+)
- 결론 (밑줄)
- 관련 차트 2~3개의 전후 해설
#
# ▸ 다단계 인과 체인 템플릿 (v12, SMIC 89점 핵심)
#   SMIC이 89점을 받는 핵심: 5~8페이지에 걸친 다단계 인과 논증.
#   필수 구조:
#     대전제: 산업 메가트렌드 (전술한 산업분석과 연결)
#       → 소전제: 동사만의 차별점 (기술/규모/브랜드/포지션)
#         → 근거 ①: 정량 데이터 (도표/테이블, 출처 명시)
#         → 근거 ②: 정성 논리 (경쟁/규제/기술 트렌드)
#         → 근거 ③: 크로스체크 (글로벌 사례 or 과거 사이클)
#       → 인라인 반박: "그러나~" / "다만~" → 정량적 반박 → "따라서 구조적 악재는 아님"
#       → 결론: "따라서 동사는~ 것으로 판단한다" + Bear case 하방 안전마진
#
# ▸ 과거 사이클 정량 비교 (SMIC S-Oil의 핵심 무기)
#   현재와 유사한 과거 시점을 선정, 핵심 수치 5개를 나란히 비교하는 테이블 필수.
#   S-Oil: 2015년 vs 2026년 공급과잉 규모 (113만 b/d vs 19만 b/d)
#   "15년과 현재가 유사한 국면만 가지고 있는 것은 아니다" → 차이점도 명시
#
# ▸ 글로벌 사례 크로스체크
#   미국/유럽에서 유사한 사건이 있었는지 1건 이상 필수 비교.
#
# ▸ "보수적 가정에서도 상승여력 X%" 프레이밍 (SMIC 킬러 패턴)
#   IP 결론부에 반드시 포함:
#   "본서에서는 업황 개선 미반영, 극단적 악화 가정하에서도 샤힌만으로 59% 상승여력"
#   Bear case OPM/매출을 적용해도 현재가 대비 하방 제한적임을 정량적으로 제시

## 4. 투자포인트② (5,000자+)
- (3번과 동일 구조)

## 5. 투자포인트③ (4,000자+)
- (3번과 동일 구조)
- 밸류에이션 매력이 IP인 경우: 과거 사이클 Analogy 테이블 포함

## 6. 재무분석 (6,000자+)
- 듀폰 분해: NPM × AT × EM = ROE (각 요소 연도별 변동 원인)
- 현금흐름: OCF/CAPEX/FCF 추이 + 변동 원인 서술
- 운전자본: DIO/DSO/DPO 또는 산업 특화 지표 (수주잔고/매출인식 등)
- 재무 안정성: 부채비율, ICR, 유동비율
- 배당 정책: 과거 DPS, 배당성향, 향후 전망
- ROIC vs WACC: 가치 창출/파괴 분석
- **Quality of Earnings 분석 (v9, CFA/글로벌 IB 패턴)** — 필수
  - Accruals Ratio = (NI - OCF) / Total Assets → 높으면 이익의 질 낮음
  - OCF/NI Ratio: > 1.0 건전, 0.7~1.0 주의, < 0.7 경고
  - 일회성 항목(자산처분이익, 정부보조금, 환차익 등) 분리 테이블
  - "Core Earnings" vs "Reported Earnings" 비교: 일회성 제거 후 실질 수익력 산출
  - 적용: 모든 기업 필수. 특히 영업외이익/손실이 큰 기업은 반드시
- **Earnings Surprise 차트 (v9, 한국 증권사 패턴)** — 필수 (상장 2년+)
  - 과거 8분기의 "컨센서스 EPS vs 실제 EPS" 서프라이즈 막대그래프
  - 양수(틸) = Beat, 음수(레드) = Miss
  - "과거 8분기 중 6분기 Beat → 실적 추정의 하방 신뢰도 근거"
  - 데이터: FnGuide 컨센서스 or 네이버 증권 리서치
  - 적용 조건: 상장 2년+ & 애널리스트 커버리지 3건+. 미커버리지 종목은 생략

## 7. Peer 비교 (4,000자+)
- Peer 선정 근거 (왜 이 5개사를 비교하는지)
- 멀티플 비교: PER/PBR/EV-EBITDA/OPM/ROE (각 1문장 해석)
- 차별점 vs 약점 (3개씩)
- 벤치마킹: 1등 기업의 전략에서 배울 점

## 8. 실적추정 (6,000자+)
- P×Q 사업부별 (or 수주전환율/공사진행률 기반)
  - 각 사업부 ASP/Q 추정 근거 400자+
  - 또는 프로젝트별 매출인식 타이밍
- 원가 분해: 7항목+ (자재/인건비/감가/외주/전기광열/R&D/기타)
  - 각 항목 YoY 변동 근거
- 분기별 추정표 + 해설
- Bull/Base/Bear 시나리오 (각 200자+)
- **시나리오별 매출 드라이버 분리 (v9, SMIC 로보티즈 패턴)**:
  - "같은 모델에 숫자만 바꾸기" 금지 → **드라이버 자체가 달라야 함**
  - Bear: 경쟁 심화로 점유율 침식 (예: 5%→4%)
  - Base: 현재 추세 연장 (외생변수 무변화)
  - Bull: 투자논지 100% 실현 + 추가 카탈리스트 (예: 대형 고객사 직접 도입)
  - **각 시나리오에 "전환 조건"을 명시**: "경쟁사 자제화율 50% 초과 시 Bear로 전환"
- **ASP 신뢰도 극대화 (v9, SMIC 파마리서치 패턴)**:
  - ASP는 반드시 다중 소스로 크로스체크 (공시 + 1차 조사 + Peer 가격)
  - 1차 가격조사: 최소 30건 이상 샘플 (강남언니, 네이버쇼핑, Amazon 등)
  - 지역별/채널별/제품별 가격 분포 테이블 Appendix 수록
  - "ASP X원" 한 줄이 아니라 "30병원 평균 128,042원 (최저 89,000~최고 220,000)" 형태

## 9. 밸류에이션 (5,000자+)
- WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
- 방법론 3개 (PER + PBR or EV/EBITDA + DCF)
  - 각 방법론의 선택 근거, Target 배수 근거
- Football Field
- DCF 민감도
- 확률 가중 목표주가
- 도달 경로 (2~3단계)
- **Forward PER/PBR 밴드 (v9, 한국 증권사 필수 패턴)** — 필수 (흑자기업)
  - 12MF Forward EPS = (잔여 분기 올해E + 경과 분기 내년E) 가중평균
  - X축 시간, Y축 주가, 밴드선 = 12MF EPS × PER 배수(8x/12x/16x/20x 등)
  - Historical 밴드와 나란히 배치: "과거 기준으로도 싸고, 미래 기준으로도 싸다" = 강력한 논거
  - 적용 조건: 흑자 기업 필수. 적자 기업은 Forward PSR 밴드로 대체
- **Scenario Summary 테이블 (v9, 글로벌 IB 패턴)** — 필수
  ```
  | 항목 | Bear(25%) | Base(50%) | Bull(25%) |
  | 매출 | 1.05조 | 1.20조 | 1.40조 |
  | OPM | 11.5% | 14.2% | 16.8% |
  | EPS | 4,200원 | 5,800원 | 7,500원 |
  | TP(PER) | 35,000원 | 52,000원 | 75,000원 |
  | TP(DCF) | 38,000원 | 55,000원 | 72,000원 |
  | 가중 TP | — | 51,500원 | — |
  ```
  - 시나리오별 전체 IS 요약을 한 테이블에 병렬 배치
- **Conviction Level & Position Sizing (v9, Pershing Square 패턴)** — 권장
  - High: Upside > 30% + Risk/Reward > 2.0 + 3개월 내 Catalyst
  - Medium: Upside 15~30% + Risk/Reward > 1.5
  - Low: Upside < 15% or Risk/Reward < 1.5
  - 표지에 "Conviction: HIGH" 뱃지 + Risk/Reward 비율 표시
#
# ▸ Target Multiple 선정 3단계 (v12, SMIC 표준)
#   "왜 이 배수인가"를 3단계로 명시적으로 분해:
#   ① 역사적 밴드: 과거 5년 PER/PBR 평균·중앙값·표준편차
#   ② Peer 평균: 글로벌 포함 Peer 5~10개의 평균/중앙값
#   ③ 프리미엄/디스카운트 근거: 동사의 성장률 갭, ROE 갭, 리스크 차이
#   S-Oil 원문: "Historical PBR Method를 통해 도출한 Target PBR Multiple 1.5x를
#   27E BPS 86,067원에 곱해 목표주가 128,400원을 산출했다."
#
# ▸ 방법론 선택 + 배제 근거 (SMIC 패턴)
#   "왜 이 방법론인가" + "왜 다른 방법론을 안 쓰는가" 양쪽 명시.
#   S-Oil: "정유 산업은 원유가에 민감하여 4~7년 사이클 → DCF 부적합 → PBR 선택"
#   S-Oil: "Peer PBR 미적용 이유: ① 기업별 사이클 Phase 상이 ② 순수 정유사 부재"
#
# ▸ "보수적 가정 명시" 패턴
#   밸류에이션 결론에 반드시 포함:
#   "업황 개선 미반영, 극단적 악화 가정(Bear case OPM X%)에서도 상승여력 Y%"

## 10. 리스크 (4,000자+)
- 리스크 5~6개 (각 300자+)
- EPS 민감도 정량화 (변수별 ±영향)
- 최악 시나리오 합산 → Bear Case 검증
- 모니터링 체크포인트 5개
- 리스크 대비 업사이드 비교
- **Catalyst Timeline (v9, 헤지펀드 패턴)**: 향후 12개월 주요 촉매 이벤트 캘린더
  - `svg_timeline()` 활용: 수평 타임라인에 Q별 이벤트 배치
  - 각 이벤트에: 예상 시점 / Bull or Bear 영향 / 주가 영향 추정(%)
  - 예: "Q2 실적발표(+5~10%) → Q3 신제품 출시(+3%) → Q4 MSCI 리밸런싱(+2~5%)"
  - 기존 `svg_timeline()`은 과거 이벤트 → 이건 **미래 촉매 전용**
- **Kill Conditions (v9, 헤지펀드 패턴)**: 투자논지 사망 조건 리스트
  - 모니터링 체크포인트와 다름: 체크포인트 = "관찰 대상", Kill Condition = **"이게 발생하면 게임 오버"**
  - 테이블: Kill Condition / 트리거 수치 / 현재 수치 / 마진(여유도) / 모니터링 주기
  - 예: "OPM < 10% 2분기 연속" / 현재 13.2% / 여유 3.2%p / 분기별
  - 최소 3개 이상 (투자포인트당 1개)
- **3-Stop 리스크 관리 전략 (v13.2, Jeff Sun 패턴)**
  - 1R 리스크가 아닌 **최대 -0.67R로 손실 제한**하는 3단계 스탑 전략
  - Stop 1: 초기 스탑 (1R 위치) — 전체 포지션의 1/3 정리
  - Stop 2: LoD + ATR 거리 — 추가 1/3 정리
  - Stop 3: 최종 이탈 — 잔여 포지션 정리
  - 결과: 풀 스탑 시에도 -1R이 아닌 -0.67R로 제한
  - **CUFA 적용**: Kill Condition 도달 시 즉시 전량 매도가 아닌 3단계 분할 이탈 권장
- **포지션 사이징 (v13.2, Jeff Sun 패턴)**
  - ADR%(Average Daily Range %) 기반: 변동성 높은 종목 = 작은 포지션
  - 포지션 크기 = 허용 리스크(%) ÷ ADR%
  - 총 포트폴리오의 1% 리스크 기준, ADR% 5% 종목 = 20% 포지션, ADR% 10% 종목 = 10% 포지션
  - **CUFA 적용**: 보고서 리스크 섹션에 "권장 포지션 사이즈" 1줄 추가 (ADR% 기반)
- **핵심 원칙: "절대 2주 수익을 하루에 잃지 마라"** → Kill Condition + 일일 손실 한도(-2%)로 구현
- **시장 국면 분석 (v13.2, Jeff Sun Top-Down 패턴)**
  - 산업분석 도입부에 현재 시장 국면 1단락 추가:
  - Level 1: 시장 폭(breadth) — KOSPI 200 종목 중 20일선 위 비율
  - Level 2: 지수 이격 — ATR% 기준 과매수/과매도 판단
  - Level 3: 섹터 상대강도 — 해당 섹터의 RS 위치
  - Level 4: 산업군 — 해당 산업군의 1개월 RS 신고가 여부
  - "현재 시장은 [국면]이며, 동사가 속한 [섹터]는 상대강도 [X]로 [판단]이다."

## 11. Appendix (3,000자+ 해설 + 테이블 16개+)
- A-1~A-16 필수 (연결6+별도5+공통5): IS_CFS/BS_CFS/CF_CFS/원가판관비/금융손익/법인세 + IS_OFS/BS_OFS_CF/금융손익_OFS/원가판관비_OFS/무형자산상각 + 주당지표/P×Q확장/DCF_WACC상세/Peer비교/투자체크리스트
- **TP Revision History (v9, 한국 증권사 패턴)** — 필수
  - 테이블: 날짜 / 투자의견 / 목표주가 / 변경 사유
  - 첫 보고서면 1행("신규 커버리지 개시"), 업데이트면 이전 TP와 비교
  - 예: "2026.03.28 | BUY | 52,000원 | 신규" → "2026.06.30 | BUY | 58,000원 | Q2 실적 서프라이즈"
- **Compliance Notice 상세 (v9, 필수)**
  ```
  본 보고서는 충북대학교 가치투자학회(CUFA)의 학술 연구 목적으로 작성되었으며,
  특정 종목의 매수/매도를 권유하지 않습니다.
  모든 투자 판단과 책임은 투자자 본인에게 있습니다.
  AI 도구(Claude Code + Nexus MCP)가 데이터 수집 및 보고서 작성을 보조하였으며,
  모든 투자 판단과 최종 검증은 학회원이 수행하였습니다.
  데이터 출처: DART, ECOS, KRX, FRED 등 공개 소스.
  ```
  - 작성자별 해당 종목 보유 여부 테이블 필수
  - HTML 자동 삽입
- 각 테이블 전에 1~2줄 해설
```

**합계: 58,000자+ (마크다운 본문만). HTML 변환 시 차트 해설·callout·expand 추가로 75,000자+ 달성.**

### 8-0b. "아무것도 모르는 사람도 이해하게" 쓰는 법

SMIC S-Oil 보고서가 89점인 핵심 이유: **정유업을 모르는 사람도 읽고 투자 판단을 내릴 수 있다.**

적용 규칙 (Evaluator 검증 가능하게 구체화):
1. **전문용어 첫 등장 시 반드시 정의**: "OPM(영업이익률, Operating Profit Margin)"
   - 검증: Glossary에 10개+ 용어 정의 존재 여부로 체크
2. **비유로 설명**: 산업 기초 설명에 최소 3개 비유 포함
   - 검증: "~와 같다", "~에 비유하면", "마치 ~처럼" 패턴 3건+ 존재
3. **숫자에 맥락 부여**: 모든 핵심 수치에 비교 대상 제시
   - 검증: "GDP의 ~%", "~대비", "~에 해당" 패턴 10건+
4. **투자 귀결 문장**: 모든 분석 문단(sidebar-layout 내 content-area)의 마지막 문장이 투자 판단과 연결
   - 검증: 각 sidebar-layout 블록의 마지막 <p>에 "주가", "밸류에이션", "EPS", "매출", "투자" 등 투자 키워드 포함
5. **산업 기초 2,000자+ 필수**: 섹션1과 섹션2에서 산업의 구조·수익 모델·핵심 용어를 먼저 설명
   - 검증: 섹션1+2 합산 글자수 16,000자+
6. **도표 밀도 최소 기준**: 섹션당 최소 SVG 4개 + 테이블 2개
   - 검증: 11섹션 × (4 SVG + 2 테이블) = SVG 44개 + 테이블 22개 이상
   - 이 기준이 SVG 50개 HARD MIN의 근거

### 8-1. 아키텍처 (v8)

```
Phase 1 산출물: {종목명}_CUFA_본문.md (마크다운, 75K자+)
Phase 2 산출물: build_{종목명}.py (Python, 헬퍼 재사용)
Phase 3 산출물: {종목명}_CUFA_보고서.html (인터랙티브 HTML, 250KB+)
```

단일 파일 내 구조:
1. **글로벌 도표 카운터** (`_fig_counter`, `fig_num(sec)`)
2. **SVG 헬퍼 함수** (11종 — 아래 참조)
3. **`table()` 헬퍼** — 도표 번호 + 출처 지원
4. **`gen_css()`** — 다크테마 CSS 전체
5. **`gen_cover()`** — 커버 (IS 7열: 2022A~2028E)
6. **`gen_toc()`** — 앵커 링크 TOC (페이지번호 X)
7. **`section_header(num, title)`** — "Equity Research Report | 종목명" 서브헤더 + id
8. **`sidebar_wrap(kws, content)`** — 2열 레이아웃 래퍼
9. **`gen_section1()` ~ `gen_section11()`** — 11개 섹션
10. **`gen_footer()`** + **`build()`** — 조립 + 검증

### 8-2. SVG 헬퍼 함수 16종

**기존 12종 (v4)**

| 함수명 | 용도 | 핵심 파라미터 |
|--------|------|---------------|
| `svg_bar()` | 수직 막대 | labels, values, colors, show_line, sec, unit |
| `svg_line()` | 라인 차트 | labels, datasets[(name,vals,color)], sec, unit |
| `svg_donut()` | 도넛 차트 | segments[(label,val,color)], sec |
| `svg_hbar()` | 수평 막대 | labels, values, sec |
| `svg_waterfall()` | 워터폴 | items[(label,val,type)], sec |
| `svg_scatter()` | 산점도 | points[(name,x,y,color,size)], sec |
| `svg_football()` | 풋볼 필드 | rows[(method,low,high,color)], current, sec |
| `svg_heatmap()` | 히트맵 | row_labels, col_labels, 2D data, sec |
| `svg_grouped_bar()` | 그룹 막대 | labels, group_names, group_data, sec |
| `svg_bubble_risk()` | 리스크 매트릭스 | risks[(name,prob,impact,color,sz)], sec |
| `svg_per_band()` | PER 밴드 | years, prices, per_levels, sec |
| `svg_flow_diagram()` | 플로우 다이어그램 | stages[(label,sublabel,color)], sec |

**신규 4종 (v5)**

| 함수명 | 용도 | 핵심 파라미터 | 벤치마크 출처 |
|--------|------|---------------|-------------|
| ~~`svg_radar()`~~ | ~~레이더/스파이더 차트~~ | ~~삭제됨 (v13)~~ | **금지**: feedback_no_radar.md |
| `svg_area()` | 누적 면적 차트 | labels, datasets[(name,vals,color)] | 매출 구성 추이 |
| `svg_timeline()` | 수평 타임라인 | events[(date,desc,color)] | YIG 키움 (자사주 소각 스케줄) |
| `svg_comparison_matrix()` | 비교 매트릭스 | row_labels, col_labels, 2D data, colors | SMIC 알지노믹스 (경쟁약물 비교) |
| `svg_annotated_price()` | 이벤트 주석 주가 차트 | dates, prices, events[(date,label,color)], sec | YIG 키움증권 (6개 이벤트 매핑) |
| `svg_tam_sam_som()` | TAM/SAM/SOM 동심원/퍼널 | levels[(label,value,color)], sec | SMIC 로보티즈 (액츄에이터 시장) |

모든 함수 공통:
- `sec` 파라미터 → 자동 "도표 X-Y." 프리픽스
- `style="width:100%;max-width:700px;"` 반응형 (도넛은 500px)
- Y축 그리드라인(점선) + **Y축 라벨(값)** 기본 포함
- `unit` 파라미터 → "(단위: 억원)" 자동 표시
- `add_source(chart_html, src)` 함수로 출처 추가
  - **주의**: `rfind('</div>')` 사용 — 마지막 `</div>` (chart-box 닫기) 앞에 삽입
- **hover 효과**: CSS `transition + filter:brightness(1.2)` 자동 적용 (rect/circle)

### 8-2b. v5 CSS 컴포넌트

| 클래스 | 용도 | 사용 예시 |
|--------|------|----------|
| `.callout` | 핵심 메시지 강조 박스 (보라 좌측 바) | 섹션 결론, 목표주가 선언 |
| `.insight-box` | 인사이트/시사점 박스 (초록 테두리) | 차트 해석 후 시사점 |
| `.progress-bar > .fill` | 프로그레스 바 | 시너지 실현률, 목표 달성률 |
| `.table-scroll` | 넓은 테이블 스크롤 래퍼 | Appendix 7열+ 테이블 |
| `.section-divider` | 섹션 간 구분선 | 대섹션 전환 |
| `tabular-nums` | 테이블 숫자 정렬 | 자동 적용 (td:not(:first-child)) |

**반응형**: `@media (max-width:768px)` — cover/sidebar/chart-pair/metric-grid 자동 1열 전환
**인쇄**: `@media print` — 배경 흰색, page-break-inside:avoid, A4 마진 2cm

### 8-3. 표준 섹션 구조 (11개)

```
섹션  | 제목                          | 핵심 내용
------|-------------------------------|------------------------------------------
1     | 기업 개요                      | 산업 기초, 장비 종류, 역사, 사업부×5 상세, MLA 밸류체인
2     | 산업 분석                      | 시장 구조/동인, 지역별, 경쟁구도, 전동화/자율주행
3     | 투자포인트 ①                   | 핵심 시너지/차별화, DSA 아키텍처 다이어그램
4     | 투자포인트 ②                   | 글로벌 확장, 지역별 경쟁환경 상세
5     | 투자포인트 ③                   | 밸류에이션 매력, Re-rating 트리거, MSCI
6     | 재무 분석                      | 듀폰 분해, 운전자본(DIO/DSO/DPO), 분기마진, ROIC vs WACC
7     | Peer 비교                      | OPM vs PER 산점도, 벤치마킹
8     | 실적 추정 (P×Q)               | 사업부별 ASP×Q, 분기별 추정, Bull/Base/Bear
9     | 밸류에이션                      | WACC 산출 상세, PER/EV-EBITDA/DCF, Football Field
10    | 리스크 분석                     | EPS 민감도 정량화, 리스크 매트릭스, 모니터링 체크포인트
11    | Appendix                       | A-1~A-16 (연결6: IS/BS/CF/원가판관비/금융손익/법인세 + 별도5: IS/BS_CF/금융손익/원가판관비/무형자산 + 공통5: 주당/P×Q/DCF_WACC/Peer/체크리스트)
```

### 8-4. 각 섹션 코드 패턴

```python
def gen_sectionN():
    h = section_header(N, "섹션 제목")
    kws = [("키워드1", "값1"), ("키워드2", "값2"), ...]  # 4~6개
    txt = """
    <p><strong>Bold 도입문으로 핵심 주장 선언.</strong> 보통체로 근거 전개...</p>
    <p>추가 분석 단락...</p>
    <p><strong><u>핵심 결론은 볼드+밑줄로 강조.</u></strong></p>
"""
    h += sidebar_wrap(kws, txt)
    # 차트/테이블은 sidebar_wrap 밖에 배치
    h += '<div class="chart-pair">\n'
    h += add_source(svg_bar("제목", labels, values, sec=N, unit="억원"))
    h += add_source(svg_donut("제목", segments, sec=N))
    h += '</div>\n'
    h += table(headers, rows, highlight_rows={...}, sec=N, title="테이블 제목", src="출처")
    h += '</div>\n'
    return h
```

### 8-5. 검증 기준

| 항목 | 목표 | 비고 |
|------|------|------|
| 텍스트 | 60,000~80,000자 | 컴팩트 but 실질적. 무의미한 반복 금지 |
| SVG 차트 | 50+ | 섹션당 최소 4개 (HARD_MIN) |
| 테이블 | 30+ | 특히 Appendix에 집중 |
| 도표 번호 | 전수 | "도표 X-Y." 형식 |
| 출처 | 전수 | 모든 차트/테이블 하단 |
| sidebar | 전 섹션 | 4~6개 키워드+수치 |
| 파일 크기 | 200KB+ | — |

### 8-6. 종목 교체 시 수정 포인트

새 종목으로 보고서를 만들 때 수정해야 할 부분:
1. `gen_cover()` — 종목명, 투자포인트 3개, IS 데이터, 사이드바 메트릭스
2. `gen_toc()` — 섹션 제목 조정 (투자포인트 내용에 따라)
3. `gen_section1()` — 기업 개요, 사업부 구조, 역사
4. `gen_section2()` — 해당 산업 분석 (산업별 완전 재작성)
5. `gen_section3~5()` — 투자포인트 (종목별 완전 재작성)
6. `gen_section6()` — 재무 데이터 교체 (DART 기반)
7. `gen_section7()` — Peer 그룹 교체
8. `gen_section8()` — P×Q 매출추정 (사업부 구조에 따라)
9. `gen_section9()` — WACC 파라미터, 밸류에이션 수치
10. `gen_section10()` — 종목별 리스크 요인
11. `gen_section11()` — 재무 데이터 교체

헬퍼 함수(svg_*, table, CSS, section_header, sidebar_wrap)는 **재사용** — 수정 불필요.

### 8-7. 서술 원칙 (SMIC 스타일)

- **비유적 섹션 제목 (v9, SMIC 벤치마크)**: 호기심 유발 + 스캔 리딩 최적화
  - 예: "흐르는 주가를 거꾸로 거슬러 오르는 연어" (파마리서치), "액츄에이터 수요의 Big Wave" (로보티즈)
  - 각 투자포인트 제목은 **핵심 메시지를 은유적으로** — "ODM에서 브랜드로: 한국콜마의 조용한 변신"
  - 산업분석 소제목도 질문형 활용 — "휴머노이드, When? How Many?"
  - 사이드바 키워드와 연결: 비유적 제목 → 사이드바에 핵심 수치 → 본문에 근거
#
# ▸ 섹션 네이밍 공식 (v12, SMIC 표준)
#   패턴: [번호]. [캐치프레이즈] — [섹션 유형]
#   SMIC 실제 목차:
#   - "1. 정유·석유화학 산업 톺아보기 — 산업분석"
#   - "3. Super Shaheen ♬ — 투자포인트 ①"
#   - "5. 윤활유는 절대 죽지 않아 — Plus α"
#   - "2. 흐르는 주가를 거꾸로 거슬러 오르는 연어 — 산업/기업분석"
#   - "3. 리쥬란, 믿어쥬란 — 투자포인트 1"
#   네이밍 유형 3종:
#   ① 은유형: 본질 비유 ("바다 위의 파이프라인", "K-POP의 정석")
#   ② 질문형: 호기심 유발 ("뒷배가 아람코?", "OPM 반등은 가능한가?")
#   ③ 패러디형: 작품/유행어 차용 ("『무한성』장으로 진격의 서프라이즈")
#   gen_toc()와 section_header()에 캐치프레이즈가 표시되도록 구현.
- **산업 기초부터 설명**: 장비 종류, 시장 구조, 가격 결정 구조, 유통 구조, 수명 주기 등
  - 처음 보는 사람도 산업을 이해할 수 있어야 함
  - 일반 리서치 보고서(전문가용)와 차별화되는 핵심
- **P×Q 방식 매출추정**: 사업부별 ASP × 수량 = 매출, 각 추정 근거 400자+
- **WACC 산출 과정 명시**: Rf, β, ERP, Ke, Kd, D/E 각 파라미터 선정 근거
- **리스크 정량화**: 각 리스크의 EPS 영향도(원) 산출
- **Bold 도입문 → 보통체 근거 → 밑줄 결론** 패턴 일관 적용
- **비문·불필요 내용·분량 뻥튀기 절대 금지**:
  - 비문 유형: 주어-서술어 불일치, 조사 오류, 문장 미완성, 번역투("~에 의해", "~것이 되다")
  - 애매한 서술 금지: "~할 것으로 판단된다", "~할 가능성이 있다" → "~이다", "~한다"
  - 공허한 수식어 금지: "매우", "상당히", "크게" → 정량화("32.4%", "1.2배")
  - 일반론 금지: "ESG가 중요하다", "디지털 전환이 가속화되고 있다" → 구체적 데이터 없으면 삭제
  - 중복 서술 금지: 같은 내용이 2번 이상 나오면 1곳만 남기고 삭제
  - "~하였다" 과거형 남발 금지 → "~한다/~이다" 현재형 단정체로 통일
  - "~것으로 전망된다/판단된다/예상된다" 금지 → "~할 것이다/~이다"
  - "에서...에서" 조사 중복 금지
  - "~에 의한" 번역투 금지 → "~이 만든/~이 초래한"
  - "흥미로운/주목할 만한" 등 filler 수식어 금지 → 구체적 수치로 대체
  - Appendix에 교과서 정의 금지: "포괄손익계산서는 기업의..." 같은 교과서 설명 절대 불필요
  - **수치 일관성 필수**: 동일 데이터(EPS/OPM/매출)가 표지·본문·Appendix에서 다르면 Evaluator 즉시 실패
    - 표지 IS 요약, 본문 서술, sidebar, Key Charts, Appendix 테이블 — 전부 동일해야 함
    - 연도 표기 오류 특히 주의: 2025E vs 2026E 헷갈리지 말 것
  - **분량보다 밀도**: 자수 목표에 집착하지 말 것. 의미 없는 문장 추가로 분량 채우기 = 실패
- **문단 길이 균일화** (SMIC 벤치마크):
  - 목표: 문단당 200~400자 (SMIC 평균)
  - 800자 이상 문단 금지 → 2개로 분할
  - 50자 이하 문단 금지 → 앞뒤 문단에 병합
  - Evaluator가 문단 길이 편차(표준편차) 자동 체크 → σ > 200이면 경고
- **P×Q 5개년(2024A~2028E)**: Appendix A-13에 사업부별 ASP/Q를 5개년 전체로 제시

### 8-7a. 문체 자동화 규칙 (v13, 15편 역설계 실측 기반)

> 2026.04.03 역설계 분석 완료. SMIC 5편 + YIG 7편 + STAR 2편 + 리튼 1편 실측 데이터 기반.
> 핵심 발견: **분량≠품질**. CUFA 평균 104K > SMIC 평균 82K이지만 SMIC이 S등급. 밀도가 핵심.

#### 8-7a-1. 페이지 밀도 기준 (SMIC 실측, v13 최우선)

**SMIC 한 페이지의 정확한 구성:**
- 본문: 공백 포함 1,300자 / 공백 제외 1,000자
- 문단 수: 5개 (문단당 공백포함 260자 / 공백제외 200자)
- 시각자료: **매 페이지 반드시 1개 이상** (텍스트만의 페이지 금지)
- 시각자료는 해당 페이지 문단 내용을 직접 뒷받침하는 것

**SMIC 표지 서머리:**
- 공백 포함 1,000자
- 포괄손익계산서 8개년(2021A~2027E): 매출/YoY/원가/GPM/판관비/영업이익/OPM/기타/금융/법인세/당기순이익/NPM 전부 포함
- Key Financials + 12M 주가차트 + 투자포인트 3줄 요약

**Evaluator 체크 (v13 신규):**
```python
# 문단 길이 검증 (공백 제외 기준)
for para in paragraphs:
    chars_no_space = len(para.replace(' ', '').replace('\n', ''))
    if chars_no_space > 400:  # 공백제외 400자 초과 = 분할 필요
        warn(f'문단 과대: {chars_no_space}자 → 200자 내외 2개로 분할')
    if chars_no_space < 80:   # 공백제외 80자 미만 = 병합 필요
        warn(f'문단 과소: {chars_no_space}자 → 앞뒤 문단에 병합')
```

#### 8-7a-2. 종결어미 패턴 (SMIC 실측 분포)

| 패턴 | 비율 | 용도 | 예시 |
|------|------|------|------|
| **~이다/~다** | 50% | 사실 서술 | "동사의 OPM은 41.3%다." |
| **~한다/~된다** | 25% | 분석 전개 | "이는 구조적 마진 개선을 의미한다." |
| **~것으로 판단한다** | 15% | 의견 제시 | "본서는 25E OPM 42%를 달성할 것으로 판단한다." |
| **~전망이다/~예정이다** | 10% | 미래 전망 | "26E 매출 7,235억원 전망이다." |

**금지 표현 (Evaluator 자동 탐지):**
```python
WEAK_ENDINGS = [
    r'할 것으로 기대된다',     # → "~할 것이다" 또는 "~것으로 판단한다"
    r'할 수도 있다',          # → "~할 가능성이 있다(X%)" 또는 삭제
    r'할 것으로 보인다',       # → "~것으로 판단한다"
    r'인 것으로 사료된다',     # → "~이다" 또는 "~것으로 판단한다"
    r'할 것으로 예상된다',     # → "~전망이다" 또는 "~것으로 판단한다"
    r'않을까 싶다',           # 삭제. 애매한 추측 금지
]
```

#### 8-7a-3. 호칭 체계 (실측 빈도)

| 표현 | SMIC 빈도 | 용도 | 규칙 |
|------|-----------|------|------|
| **"동사(同社)는"** | 118회/편 (84~149) | 분석대상 기업 | **기본 호칭. 80회+/편 필수** |
| **"본서는/에서는"** | 5~8회/편 | 보고서 주체 | 의견 제시 시에만 |
| **기업명 직접** | 1~2회 | 첫등장+표지 | 본문에서 기업명 직접 사용 최소화 |

**Evaluator 체크:**
```python
dongsa_count = html.count('동사') + html.count('同社')
if dongsa_count < 80:
    warn(f'"동사" 사용 {dongsa_count}회 — 최소 80회 필요')
```

#### 8-7a-4. 볼드-첫문장 원칙 (SMIC 핵심 패턴, 338회/편)

**구조**: `**[핵심 주장 20~40자]** [근거 전개 150~250자]`

**SMIC 원문 예시:**
> "**정유사는 저질의 정제유를 고품질의 경질유로 바꾸기 위해 고도화 설비 도입을 늘리고 있다.** 고도화 설비란 원유의 잔사유 분획을 경질유 분획으로 전환하는 공정을 말한다. 대표적으로 FCC, 수첨분해(HDC), 코커(Coker) 등이 있으며..."

> "**스킨부스터는 글로벌 에스테틱 시장에서 가장 빠르게 성장하는 카테고리다.** 스킨부스터는 유효성분을 진피층에 직접 주입하여 피부 수분, 탄력, 광채를 개선하는 시술로..."

**Evaluator 체크:**
```python
# <p><strong> 또는 <p><b>로 시작하는 문단 비율
bold_start_ratio = bold_first_paras / total_paras
if bold_start_ratio < 0.80:
    warn(f'볼드 첫문장 비율 {bold_start_ratio:.0%} — 80%+ 필요')
```

#### 8-7a-5. 전환어 패턴 (실측 빈도표)

| 전환어 | 용도 | SMIC 빈도 | 목표 |
|--------|------|-----------|------|
| "전술한 바와 같이" / "전술했듯이" | 이전 섹션 연결 | 14회/편 | 10회+ |
| "그렇다면" | 질문→답변 전환 | 2~5회 | 3회+ |
| "이에 더해" / "나아가" | 추가 논점 | 6회 | 5회+ |
| "한편" | 시각 전환 | 2~5회 | 3회+ |
| "이처럼" / "이와 같이" | 소결 | 5회 | 5회+ |
| "실제로" | 사례 제시 | 10회 | 8회+ |
| "다만" | 리스크/반론 인정 | 9회 | 8회+ |
| "구체적으로" | 상세 전개 | 3~5회 | 3회+ |

**현재 CUFA: 20~25회/편 → 목표: 50회+/편 (2배 증가)**

**Evaluator 체크:**
```python
TRANSITION_WORDS = ['전술한', '전술했듯이', '그렇다면', '이에 더해', '나아가',
                    '한편', '이처럼', '이와 같이', '실제로', '다만', '구체적으로']
transition_count = sum(html.count(w) for w in TRANSITION_WORDS)
if transition_count < 50:
    warn(f'전환어 {transition_count}회 — 50회+ 필요')
```

#### 8-7a-6. 크로스레퍼런스 (SMIC 핵심 차별점, 14회/편)

**SMIC 패턴**: 섹션 간 논리 연결을 명시적으로 표현
> "[투자포인트 1]에서 전술한 것처럼 원가 우위를 바탕으로~"
> "[5. 투자포인트 2]에서 후술하겠지만~"
> "산업분석에서 살펴본 구조조정 트렌드가~"

**목표: 10회+/편**. Evaluator가 "전술한/후술할/앞서 살펴본/~에서 다룬" 패턴 카운트.

#### 8-7a-7. 원문자(①②③) 체계

**필수**: 복수 논점(3개+) 나열 시 반드시 원문자 사용
```
"본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다.
① 공정 구조의 차이 ② 글로벌 공급 과잉 압력 완화 ③ 아람코의 전략적 의도"
```

**금지**: `1., 2., 3.` 또는 불렛(•) 혼재. YIG식 로마숫자(I, II, III)는 투자포인트 대제목에만 허용.

#### 8-7a-8. 차트 유형 목표 분포 (v13)

| 유형 | 비율 | SVG 함수 | 용도 |
|------|------|----------|------|
| 라인 차트 | 30% | `svg_line()` | 시계열 추세 (주가, 매출, OPM) |
| 막대 차트 | 25% | `svg_bar()`, `svg_grouped_bar()` | 비교, 구성비, YoY |
| 면적 차트 | 10% | `svg_area()` | 누적 매출, 시장 점유율 추이 |
| 산점도 | 5% | `svg_scatter()` | OPM vs PER, ROE vs PBR |
| 히트맵 | 5% | `svg_heatmap()` | DCF 민감도 (WACC × g) |
| 워터폴 | 5% | `svg_waterfall()` | 비용 분해, Bridge |
| 테이블 | 15% | `table()` | 재무 데이터, Peer 비교 |
| 기타 | 5% | `svg_donut()`, `svg_bubble_risk()` | 구성비, 리스크 매트릭스 |

#### 8-7a-9. 시각자료 다양화 — SVG 외 이미지 활용 (v13 신규)

**SMIC/YIG는 SVG 차트만이 아니라 다양한 시각자료를 활용한다:**

| 유형 | 구현 방법 (HTML) | 용도 |
|------|-----------------|------|
| **기업 로고** | `<img>` 태그 + WebFetch 다운로드 | 표지, Peer 비교 |
| **제품 사진** | 기업 IR 페이지에서 다운로드 | 기업분석, 제품 설명 |
| **지도/지역도** | 인라인 SVG 직접 그리기 | 지역별 매출, 공장 위치 |
| **브랜드 이미지** | 기업 홈페이지에서 다운로드 | 브랜드 분석, 경쟁사 비교 |
| **산업 밸류체인도** | 인라인 SVG (MLA 패턴) | 산업분석 첫 장 |
| **공정/설비 도식** | 인라인 SVG 또는 다운로드 | 기술 설명 |
| **시너지 아키텍처** | 인라인 SVG (DSA 패턴) | 투자포인트 |
| **스크린샷** | WebFetch + 크롭 | 앱/서비스 UI, 뉴스 |
| **특허/논문 표지** | 다운로드 | 기술적 해자 근거 |

**구현 패턴:**
```python
# Phase 1에서 이미지 수집
# 1) 기업 로고: 기업 홈페이지 또는 DART
# 2) 제품 사진: IR 페이지 WebFetch
# 3) 지도: 인라인 SVG로 직접 구현 (viewBox 기반)
# 저장: data/images/{종목코드}_{용도}.png
# HTML 삽입: <img src="data:image/png;base64,{b64}" alt="{설명}" style="max-width:100%;">
# → base64 인코딩으로 HTML 단일 파일 유지
```

**규칙:**
- 외부 이미지 URL 직접 참조 금지 (오프라인에서도 동작해야 함)
- 모든 이미지는 base64로 인라인 삽입 또는 data/ 폴더에 저장
- 저작권 주의: IR 자료, DART 공시, 특허 공보는 인용 가능. 유료 보고서 캡처 금지
- 이미지에도 "도표 X-Y." 번호 + 출처 표기 필수

### 8-7b. 추론 깊이 체계 (v13, 역설계 핵심 발견)

> **"추론 4~5단계가 A→S의 갈림길"** — 15편 역설계 최대 인사이트

#### 등급별 추론 단계

| 등급 | 추론 단계 | 패턴 | 예시 |
|------|----------|------|------|
| **S/S+** | 4~5단계 | 트렌드→구조변화→포지셔닝→수익영향→리레이팅 | SMIC 파마리서치 |
| **A/A+** | 3~4단계 | 수요증가→매출성장→OPM개선→주가상승 | YIG HD건설기계 |
| **B/B+** | 2~3단계 | 산업성장→매출증가→주가상승 | 일반 학회 보고서 |

#### S등급 추론 체인 템플릿

**SMIC 파마리서치 (실제 추론 체인):**
```
[1단계] 글로벌 에스테틱 시장의 구조적 성장 (비침습, 고령화, 소비자 인식 변화)
  ↓ 왜 이 산업인가?
[2단계] 스킨부스터 카테고리가 에스테틱 내 최고 성장률 (CAGR 15%+)
  ↓ 왜 이 카테고리인가?
[3단계] PN(폴리뉴클레오타이드) 원천기술에서 동사 독점 → 경쟁자 진입장벽
  ↓ 왜 이 기업인가?
[4단계] 공급 제약 + 브랜드 파워 = ASP 하락 제한 → 가격결정력 유지
  ↓ 수익에 어떤 영향?
[5단계] 매출 CAGR 20%+ 유지 → Forward PER 재평가 → 목표주가 80만원
  ↓ 밸류에이션에 어떤 영향?
```

**SMIC S-Oil (실제 추론 체인):**
```
[1단계] 글로벌 정유 구조조정 → 공급 축소 (유럽/미국 NCC 전환)
  ↓
[2단계] 중동 COTC 트렌드 → 아람코 전략 = 석유 수명 연장
  ↓
[3단계] 동사 = 아람코 최대 해외 정유 투자처 → 샤힌 프로젝트 시너지
  ↓
[4단계] 고도화율 36%→53% → 경질유 비중 증가 → 마진 구조 개선
  ↓
[5단계] 정유 마진 + 석화 마진 동시 개선 → PBR 리레이팅
```

#### 투자포인트 작성 시 필수 체크

**모든 투자포인트는 작성 전에 추론 체인을 먼저 설계한다:**
```
투자포인트 ① 추론 체인:
  [1] _________ (산업/거시 트렌드)
  [2] _________ (카테고리/세그먼트 선택 이유)
  [3] _________ (기업 경쟁력/해자)
  [4] _________ (수익 영향 정량화)
  [5] _________ (밸류에이션 임팩트)
```

**Evaluator**: 각 투자포인트에 "추론 N단계" 체인이 명시적으로 드러나는지 검증.
- 3단계 이하 = 경고 ("추론 깊이 부족: 산업→매출→주가 단순 체인")
- 4단계 이상 = 통과
- 5단계 = 우수

### 8-7c. 2중 반박 구조 (v13, SMIC 핵심 패턴)

> **"2중 반박이 설득력의 핵심"** — 투자포인트 내 인라인 반박 + 별도 counter_arg 블록

#### 방식 1 — 인라인 반박 (투자포인트 본문 내, 필수)

**SMIC S-Oil 원문 예시:**
> "**그렇다면 동사의 설비 증설이 정부의 사업재편 기조와 충돌할 위험은 없는 것일까?**
> 본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다.
> ① 공정 구조의 차이 — NCC 전환 대상은 올레핀 생산 설비이나, 샤힌은 정유+BTX 통합
> ② 글로벌 공급 과잉 압력 완화 — 유럽 정유사 12곳 폐쇄(2020~2025)
> ③ 아람코의 전략적 의도 — 지분 63.4% 보유, 장기 원유 판매처 확보 목적"

**HTML 구현:**
```html
<div class="inline-rebuttal">
  <p><strong>그렇다면 [우려사항]은 없는 것일까?</strong></p>
  <p>본서는 다음과 같은 이유로 그 개연성이 매우 낮다고 판단한다.</p>
  <p>① [근거1 — 구체적 데이터] ② [근거2 — 구체적 데이터] ③ [근거3 — 구체적 데이터]</p>
</div>
```

**HARD_MIN**: 투자포인트 3개 × 인라인 반박 1건+ = **최소 3건**

#### 방식 2 — counter_arg 블록 (섹션 10 리스크, 기존 강화)

기존 counter_arg에 추가 필수 항목:
```
각 리스크에 반드시 포함:
1. 확률(%) — "발생 확률 15%"
2. 완화 요인(mitigant) — "다만 ~으로 인해 실제 영향은 제한적"
3. 모니터링 KPI — "분기별 OPM 추적, 11% 이하 시 재검토"
4. EPS 영향도(원) — "발생 시 EPS -1,200원 (현재 대비 -8.3%)"
```

### 8-7d. 산출물 정의 (v13 확정)

**산출물 3개 (DOCX 제거, HTML + Excel + Markdown):**

| 산출물 | 파일명 | 용도 | 핵심 |
|--------|--------|------|------|
| **HTML** | `{종목명}_CUFA_보고서.html` | 인터랙티브 보고서 | 다크테마, SVG+이미지, 반응형, 250KB+ |
| **Excel** | `{종목명}_재무데이터.xlsx` | 재무 모델 + 데이터 | 15시트, 모든 숫자의 Single Source of Truth |
| **Markdown** | `{종목명}_CUFA_본문.md` | 텍스트 원본 | 60K자+, Phase 1 산출물, 순수 텍스트 |

### 8-8. 섹션당 최소 밀도 + 중복 방지 규칙

**콘텐츠 밀도 퇴보 방지** (감사 결과: 최신 보고서일수록 SVG/테이블이 줄어드는 문제 발견)

| 섹션 | 최소 글자수 | 최소 SVG | 최소 테이블 | 최소 사이드바 | 합계 근거 |
|------|-----------|---------|-----------|------------|---------|
| 0. Main Idea | 500 | 1 (구조도) | 1 (핵심 지표) | 0 | - |
| 0-1. 주가분석 | 3,000 | 2 (1년 일봉 + 구간) | 1 (구간 요약) | 3 | - |
| 1. 기업개요 | 3,000 | 2 | 1 | 3 | 핵심만 압축. 뻔한 연혁/ESG 금지 |
| 2. 산업분석 | 10,000 | 8 | 3 | 10 | 여기가 보고서의 기반. 깊이 있게 |
| 2-1. 기업분석 | 8,000 | 5 | 2 | 8 | 사업부 구조, 경쟁력, 해자 |
| 3. 투자포인트① | 5,000 | 3 | 1 | 5 | - |
| 4. 투자포인트② | 5,000 | 3 | 1 | 5 | - |
| 5. 투자포인트③ | 4,000 | 2 | 1 | 4 | - |
| 6. 재무분석 | 6,000 | 4 | 3 | 6 | - |
| 7. Peer 비교 | 4,000 | 3 | 2 | 4 | - |
| 8. 실적추정 | 6,000 | 4 | 3 | 6 | - |
| 9. 밸류에이션 | 5,000 | 6 (PER Band, PBR Band, Football Field, 민감도, 시나리오, Peer 산점도) | 3 | 5 | - |
| 10. 리스크 | 4,000 | 2 | 2 | 4 | - |
| 11. Appendix | 5,000 | 2 | 16 (A-1~A-16) | 0 | - |
| **합계** | **63,500** | **42** | **38** | **58** | 60K+ 필수 충족 |

**Evaluator가 섹션별로 체크**: 어떤 섹션이든 최소 기준 미달이면 경고. 전체 합계가 HARD MIN 미달이면 빌드 실패.

같은 데이터를 여러 형식(차트+테이블+도넛)으로 반복하지 말 것.

| 데이터 | 본문 시각화 | Appendix | 금지 |
|--------|------------|----------|------|
| 사업부 매출 비중 | 도넛 1개 | — | 바+도넛+테이블 3중 |
| 지역별 매출 | 바 차트(성장률 오버레이) | 테이블 | 도넛 추가 |
| EPS 추이 | 바 차트 1개 | A-4 주당지표 테이블 | 동일 차트 반복 |
| Peer PER | 산점도(OPM vs PER) | A-7 Peer 상세 테이블 | hbar 추가 |
| WACC 파라미터 | 섹션9 산출 테이블 | A-14 민감도 테이블 | 동일 테이블 복제 |
| P×Q | 섹션8 단년(2026E) | A-13 5개년 확장 | 동일 연도 데이터 반복 |

원칙: **본문은 핵심 1~2개 시각화, Appendix는 상세 테이블로 차별화.**

### 8-9. MLA/DSA 다이어그램 구현 패턴

두 다이어그램은 `svg_flow_diagram()` 헬퍼가 아닌 **인라인 SVG로 직접 구현**한다.

**MLA (밸류체인 계층도, 섹션1):**
- viewBox="0 0 700 420", 5-Layer 수직 구조
- Layer 1(원자재)→2(생산)→3(브랜드)→4(유통)→5(서비스/AM)
- 각 레이어: 가로 600px rect, 세로 간격 85px, ↑ 화살표 연결
- 레이어별 색상: 원자재(#FF4D4D), 생산(#7C6AF7), 브랜드(#A78BFA), 유통(#00E09E), AM(#FFB84D)
- 레이어 안에 핵심 텍스트 + 수치(시너지 금액 등)

**DSA (시너지 시스템 아키텍처, 섹션3):**
- viewBox="0 0 700 280"
- 좌측: 4개 입력 박스(구매통합/CAPEX/R&D/매출시너지)
- 중앙: 합산 박스(시너지 3,000억원)
- 우측: 결과 체인(OPM → EPS → 목표주가) 3단계
- 입력→합산: 수렴 라인, 합산→결과: → 화살표 연결
- **MLA 순서**: 반드시 Layer 1(원자재)이 맨 위, Layer 5(서비스)가 맨 아래. 화살표는 ↓ 방향.

### 8-10. cufa-diagram 스킬 연동

고품질 PNG 다이어그램이 필요할 때 `cufa-diagram` 스킬을 사용한다.
경로: `~/.claude/skills/user/cufa-diagram/`

- SVG 템플릿 6종(MLA, DSA, Cover, Peer, Football Field, Risk Matrix) 제공
- 9색 컬러 팔레트 + 다크 테마 CSS (`widget_base.css`)
- `python svg_to_png.py input.svg output.png` → Playwright 브라우저 렌더링으로 Retina 2x PNG
- 최초 1회: `npx playwright install chromium && npx playwright install-deps chromium`
- HTML 인라인 SVG와 별개로, 보고서 삽입용 PNG가 필요할 때 사용

## 9. 벤치마크 기반 필수 품질 기준 (v13, 15편 + 등급 체계)

2026.04.03 기준 5개 대학 투자학회 보고서 15건을 정밀 역설계하여 도출한 품질 기준.
분석 원본: `~/Downloads/STAR_YIG/` (PDF/DOCX 원본 + 변환 md/txt)

### 9-0. 벤치마크 보고서 총람 (v13 확장, 15편)

#### 학회별 요약

| 학회 | 보고서 수 | 유형 | 평균 글자수 | 등급 범위 | 핵심 강점 |
|------|-----------|------|------------|----------|----------|
| **SMIC** (서울대) | 5건 | 기업분석 | **82,268** | S~S+ | 재무 정확성, 현지화, 밸류에이션 다양성 |
| **YIG** (연세대) | 7건 | 기업분석 | **55,590** | A~A+ | 효율적 구조, 산업 깊이, 차트 풍부 |
| **S.T.A.R** (성균관대) | 2건 | 산업+기업 | **62,271** | A- | 기술/과학 깊이, 거시-미시 연결 |
| **CUFA** (충북대) | 2건 | 기업분석 | **103,755** | B+ | 분량 최대, 구현 진행 중 |
| **리튼** (이화여대) | 1건 | 기업분석 | **48,896** | B+ | 표지 데이터 밀도 우수 |

#### 전수 목록 (15편, 등급순)

| # | 학회 | 종목 | 글자수 | 등급 | 밸류에이션 | 비고 |
|---|------|------|--------|------|-----------|------|
| 1 | SMIC | 파마리서치 | 95,332 | **S+** | Historical PER | 의사 9명 인터뷰, 168건 크롤링 |
| 2 | SMIC | 애니플러스 | 77,908 | **S** | Hist. Peer PER | 회귀분석 R²=0.94, OSMU |
| 3 | SMIC | S-Oil | 73,563 | **S** | Historical PBR | 정유마진 구조 독자 분해 |
| 4 | YIG | 키움증권 | 53,778 | **A+** | PBR 비교분석 | CIR 효율성, MAU 268만 |
| 5 | YIG | HD현대건설기계 | 69,670 | **A** | DCF + PER | KEYSS팀, 산업분석 극대화 |
| 6 | YIG | HD현대중공업 | 67,727 | **A** | PER + EV/EBITDA | SOKHA팀, 지정학 연결 |
| 7 | YIG | 심텍 | 56,194 | **A** | DCF + PBR | 반도체 PCB, 투자포인트 이원화 |
| 8 | YIG | 삼성전기 | 45,742 | **A** | PBR 기반 | MLCC/FC-BGA 분석 |
| 9 | YIG | 엘앤에프 | 40,262 | **A** | DCF + EV/EBITDA | 2차전지, ESS |
| 10 | STAR | GaN반도체 | 67,232 | **A-** | 상대가치 | 산업분석 특화, 기술 깊이 |
| 11 | STAR | 중국반도체굴기 | 57,310 | **A-** | 정성분석 | 규제/정책 프레임 |
| 12 | YIG | 씨어스테크놀로지 | 55,756 | **B+** | PSR | 의료AI, Strong Buy |
| 13 | CUFA | 알지노믹스 | 90,423 | **B+** | SOTP(rNPV) | 바이오 파이프라인 |
| 14 | CUFA | 로보티즈 | 117,087 | **B+** | DCF(3-scenario) | 분량 최대, 밀도 부족 |
| 15 | 리튼 | 인텔리안테크 | 48,896 | **B+** | Historical PER | 위성통신 |

#### 핵심 인사이트: 분량 ≠ 품질

```
CUFA 평균 103,755자 (B+) > SMIC 평균 82,268자 (S등급)
→ CUFA가 2만자 더 많지만 등급은 2단계 낮음
→ 핵심은 밀도(density): 불필요한 일반론 없이 모든 문장이 투자판단에 기여하는가
```

#### 등급별 핵심 차이 매트릭스 (v13)

| 차원 | B/B+ | A/A+ | S/S+ |
|------|------|------|------|
| **추론 깊이** | 2~3단계 | 3~4단계 | **4~5단계** |
| **반박 구조** | 나열만 | 간략 반박 | **2중 반박(인라인+블록)** |
| **독자적 데이터** | 없음 | 일부 | **핵심 차별점** (인터뷰/크롤링) |
| **출처 명시율** | 60~80% | 75~90% | **95%+** |
| **문체 일관성** | 혼재 | 높음 | **매우 높음** (동사/볼드/전환어) |
| **사이드바** | 없음 | 없음 | **있음 (스캔 리딩 혁명)** |
| **크로스체크** | 0~1종 | 1~2종 | **3종+** (Reverse DCF 필수) |
| **크로스레퍼런스** | 0~5회 | 5~10회 | **10~14회/편** |
| **민감도 분석** | 없거나 부분적 | 대부분 포함 | **필수 + 히트맵** |
| **페이지당 시각자료** | 0~1개 | 1~2개 | **2~3개 (매 페이지)** |

### 9-0a. S등급 달성의 5대 핵심 요인 (v13 신규, 역설계 결론)

> 이 5가지를 모두 충족하면 S등급. 하나라도 빠지면 A등급 이하.

**1. 추론 체인 4~5단계**
- 단순 "산업성장→매출증가"(B+)가 아닌
- "트렌드→구조변화→포지셔닝→수익영향→밸류에이션 리레이팅"(S)
- 섹션 8-7b 참조

**2. 2중 반박 구조**
- 투자포인트 본문 내 인라인 반박(IP당 1건+)
- 별도 counter_arg 블록(리스크 섹션)
- 섹션 8-7c 참조

**3. 독자적 데이터**
- IR/DART는 누구나 접근 가능 → 차별화 불가
- SMIC 파마리서치: 의사 9명 인터뷰, 강남언니 시술가격 100건+, 뷰티카페 1,394건
- SMIC S-Oil: 정유마진 구조 독자 분해, COTC 수율 시뮬레이션
- **구현**: Phase 1에서 WebFetch 크롤링, 커뮤니티 데이터, 앱 리뷰 카운팅 등

**4. 사이드바 시스템 (스캔 리딩)**
- 모든 단락에 해석적 한줄 → 사이드바만 읽어도 전체 흐름 파악
- SMIC의 2단 레이아웃(65:35)이 S등급의 핵심 차별점
- 우리의 sidebar_wrap()이 이미 구현 → 키워드+수치 뿐 아니라 **해석적 메시지 1줄** 필수

**5. 크로스체크 3종+**
- 주 밸류에이션 (PER/PBR/EV-EBITDA/DCF 중 택1)
- Reverse DCF (시장 내재 성장률 역산)
- Implied PER (DCF 결과의 내재 PER 산출)
- Peer 검증 (ROE-PBR 회귀 또는 OPM-PER 산점도)

### 9-0b. HARD_MIN v14.1 (Evaluator v2 확정 기준)

**v14.1에서 evaluator.py가 자동 검증하는 확정 기준:**

| 항목 | v13 | **v14.1 (확정)** | 비고 |
|------|-----|:---:|------|
| 텍스트 | 60K자+ | **80,000자+** | Evaluator v2 HARD_MIN |
| SVG 차트 | 50개+ | **25개+** | 실측 기반 현실화 |
| 테이블 | 25개+ | **25개+** | 유지 |
| counter_arg | 3건+ | **인라인 3건+ + 블록 3건+** | 2중 반박 구조 |
| Appendix | 16개+ | 16개+ (변경 없음) | A-1~A-16 |
| 용어 정의 | 10개+ | 10개+ (변경 없음) | 비전문 독자 배려 |
| **볼드-첫문장** | - | **150개+** | Evaluator v2 bold_first_150 |
| **전환어 빈도** | - | **30회+** | Evaluator v2 transitions_30 |
| **"동사" 빈도** | - | **40~120회** | Evaluator v2 dongsa_ratio |
| **추론 깊이** | - | **IP당 4단계+** | 8-7b 참조 |
| **크로스체크 밸류에이션** | - | **3종+** | 주+Reverse DCF+Implied PER |
| **Reverse DCF** | - | **필수** | 모든 보고서에 필수 |
| **Football Field** | - | **필수** | svg_football() |
| **민감도 히트맵** | - | **필수** | svg_heatmap() WACC×g |
| **크로스레퍼런스** | - | **5회+** | Evaluator v2 cross_ref_5 |
| **출처 명시율** | - | **95%+** | 모든 차트/테이블 하단 |
| **인라인 이미지** | - | **3개+** | 로고/제품/지도 등 (8-7a-9) |
| **compliance notice** | 필수 | 필수 (변경 없음) | 투자유의사항 |
| **AI watermark** | 필수 | 필수 (변경 없음) | AI 생성 고지 |

```python
# v13 Evaluator 추가 체크
HARD_MIN_V13 = {
    'bold_first_ratio': 0.80,
    'transition_count': 50,
    'dongsa_count': 80,
    'reasoning_depth_per_ip': 4,
    'cross_check_methods': 3,
    'has_reverse_dcf': True,
    'has_football_field': True,
    'has_sensitivity_heatmap': True,
    'cross_reference_count': 10,
    'source_attribution_rate': 0.95,
    'inline_images': 3,
    'inline_rebuttal_count': 3,
    'block_rebuttal_count': 3,
}
```

SMIC 개별 보고서:

| 종목 | 페이지 | 글자수 | 도표 | Valuation | 차별점 |
|------|--------|--------|------|-----------|--------|
| 알지노믹스 | 35 | 84,334 | 82 | SOTP(rNPV) | 바이오 파이프라인 확률가중 |
| 파마리서치 | 39 | 92,769 | 56+ | Historical PER | 의사 인터뷰 9명, 168건 크롤링 |
| Sensient | 34 | 77,710 | 78 | Historical PER | 미국 주별 규제 매핑 |
| 두산 | 37 | 79,455 | 50 | SOTP(EV/EBITDA) | 지주사 Appx 19개 |
| 코오롱티슈진 | 36 | 96,831 | 36 | DCF | Bull/Bear 확률가중 |
| 풍산 | 33 | 78,892 | 35 | SOTP+PER | 포탄 물량 추정 |
| 로보티즈 | 37 | **121,420** | 35 | DCF(3-scenario) | 10년 추정, Implied PER |
| 애니플러스 | 33 | 75,872 | 34 | Hist. Peer PER | 회귀분석(R²=0.94), OSMU |
| 파마리서치v2 | 39 | 92,769 | 38 | Historical PER | (상동) |

### 9-1. 반드시 포함해야 할 구성 요소

| 요소 | 설명 | 벤치마크 출처 |
|------|------|-------------|
| **매출원가 Bottom-up 분해** | 원가율 퉁치기 금지. 원재료/인건비/감가상각/외주가공/전기광열비 등 항목별 개별 추정 | SMIC S-Oil |
| **반론 선제 논파** | Bear case를 리스크 섹션에 나열하지 말고, 해당 IP 본문에서 먼저 꺼내서 논파 ("시장이 우려하는 점은 ~이다. 그러나 ~" 패턴) | SMIC S-Oil |
| **사이드 캡션 (sidebar)** | 키워드+수치 뿐 아니라 해당 문단의 핵심 메시지 1줄을 우측에 배치. 스캔 리딩 가능하게 | SMIC 전체 |
| **과거 사이클 Analogy 테이블** | 현재와 유사한 과거 시점을 선정, 유사점/차이점을 표로 정리하여 밸류에이션 근거로 활용 | SMIC S-Oil (2015 vs 2026) |
| **Key Chart 인트로 페이지** | TOC 직후에 핵심 차트 4개를 1페이지에 모아 보고서 전체 메시지를 즉각 전달 | YIG 키움증권 |
| **용어 정리 섹션** | 비전문 독자 배려. 산업 특화 용어 10~15개를 표로 정의 | YIG 심텍/키움 |
| **P×Q 제품 세분화** | 사업부 단위가 아니라 제품 단위까지 ASP/Q 분리. 가능하면 고객사/지역별로도 분해 | YIG 심텍 (9개 제품군) |
| **수주/계약 기반 매출 인식** | 수주 기반 기업의 경우 계약건별 계약기간/분기별 매출 인식 타이밍까지 추정 | EIA 인텔리안테크 |
| **비용 추정 섹션 독립** | 매출추정과 별도로 비용추정(원가/판관비) 섹션을 분리하여 투명성 확보 | YIG 심텍/키움 |
| **이중 밸류에이션 크로스체크** | 최소 2개 방법론(PER+DCF, PBR+RIM 등)으로 교차 검증. 결과 수렴 시 신뢰도 급상승 | YIG 전체, EIA |
| **Valuation "Why X? Why not Y?"** | 선택 방법론의 근거 3문장 + 배제 방법론별 부적합 사유 1문장. SMIC 9건 전부 포함하는 핵심 패턴 | SMIC 전체 (로보티즈: "Historical 부적합—지속적자, Peer 부적합—유사기업 부재") |
| **Implied PER sanity check** | DCF 사용 시 터미널연도의 내재 PER을 산출하여 목표주가 합리성 검증. >40x = red flag | SMIC 로보티즈 (Implied PER 25.39x@30E, 9.37x@34E) |
| **지분 희석 반영** | 유상증자/CB전환/RCPS 전환 등에 따른 주식수 변동을 목표주가에 반영. 시나리오 2개 제시 권장 | SMIC 로보티즈 (유상증자), 애니플러스 (CB 콜옵션 행사/미행사 2시나리오) |

### 9-2. 논리 전개 패턴 (벤치마크 공통)

```
[산업분석] 매크로 → 산업 구조 → 경쟁 환경 → 수요/공급 동인
   ↓
[기업분석] 기업 개요 → 사업부 구조 → 기술적 해자 → 주가 이벤트 분석
   ↓
[투자포인트] IP마다: 테제 선언 → 근거 3~5개 → Bear case 선제 논파 → 결론
   ↓
[매출추정] P×Q Bottom-up (제품/고객/지역 세분화) → 분기별 인식
   ↓
[비용추정] 원가 항목별 분해 (원재료/인건비/감가상각/외주 등)
   ↓
[밸류에이션] 2개 방법론 + 민감도 + Football Field
   ↓
[리스크] 정량화(EPS 민감도) + 모니터링 지표
   ↓
[Appendix] IS/BS/CF 5개년 + P×Q 확장 + WACC + Peer + 체크리스트
```

### 9-3. 차별화된 기법 (선택 적용)

| 기법 | 설명 | 적용 상황 |
|------|------|----------|
| **독자적 분석 프레임** | 종목별 고유 개념 도입 (키움: "키움 Multiplier", HD건설기계: "시너지 실현률") | 항상 시도 |
| **Pre 투자포인트** | 본격 IP 전에 "왜 이 회사/산업인가"를 analogie로 선제 논증 | 시장 인지도 낮은 종목 |
| **ASP-변수 회귀분석** | ASP와 핵심 변수(유가, 환율 등)의 회귀식으로 ASP 추정 근거 강화 (R² 제시) | 원자재 가격 연동 기업 |
| **가동률-스프레드 시차 분석** | 과거 데이터에서 선행/후행 관계 발견하여 전망에 활용 | 시클리컬 기업 |
| **ROE-PBR 경로분석** | 과거 복수 구간의 ROE-PBR 회귀선 기울기 비교로 Target Multiple 보수성 검증 | PBR 밸류에이션 시 |
| **산업 패러다임 전환 프레임** | "Phase 1→Phase 2" 같은 거시 프레임으로 독자 관심 유도 | 산업보고서 |
| **회귀분석 매출 모델** | 외부 드라이버와 매출 간 R² 상관관계 기반 추정 (R²>0.85 시 적용). scatter+regression line SVG로 시각화, 회귀식 공개 | SMIC 애니플러스 (일본 신작 애니 수→콘텐츠 매출, R²=0.94) |
| **과거 시점 Peer (Historical Peer)** | 현재 Peer가 아닌 과거 유사 상황의 동일/유사 기업을 비교 대상으로 선정 | SMIC 애니플러스 (대원미디어 2H22를 현재 Peer 대신 선정) |
| **자회사별 개별 추정** | 사업부 단위가 아닌 연결 자회사 각각의 P×Q를 개별 추정 후 합산 | SMIC 애니플러스 (7개 자회사 개별 추정) |
| **OSMU 승수효과 정량화** | IP/콘텐츠 기업의 파생수익을 산업별 벤치마크 배수로 정량화 (Star Wars 3,200%, 평균 740%) | SMIC 애니플러스 (귀멸의 칼날 OSMU 186억원) |
| **선행지표 상관분석** | BS항목(무형자산, CapEx, 재고)과 미래 매출 간 상관계수로 실적 선행지표 식별 (R²>0.90) | SMIC 애니플러스 (무형자산→매출 R²=0.98) |
| **수요-공급 병목 체인** | 수요량→부품개수→공급량→갭 정량화로 밸류체인 병목 지점 도출 | S.T.A.R 중국 반도체 (AI칩→HBM 쇼티지 분석) |
| **유효이자율별 이자추정** | 이자발생자산/부채 항목별 유효이자율 산출 후 정밀 이자손익 추정 | SMIC 파마리서치 (자산별 weighted rate) |
| **웨이퍼-다이 수율 공식** | 반도체 보고서에서 웨이퍼당 생산 가능 다이 수를 물리 공식으로 직접 산출 | S.T.A.R GaN (r, 다이면적, 수율 기반) |
| **해외 사례 크로스체크** | 해외 유사 정책/사례를 국내 전망에 대입하여 효과 검증 (일본 신NISA→한국 밸류업, 중국 대기금→국내 반도체 투자) | YIG 키움증권, S.T.A.R (대기금 1/2/3기) |
| **보조 Multiple 이업종 검증** | Target Multiple을 단일 Peer가 아닌 사업구조 유사 이업종과도 비교하여 이중 검증. "편의점 PER 20x와 면세점 PER 25x 사이" 식의 논증 | SMIC JTC (패키지관광 × 편의점 구조 유사성) |
| **손상차손 환입 추정** | BS상 손상차손이 큰 기업의 경우, 환입 타이밍과 금액을 별도 Appendix로 추정 | SMIC JTC (관리종목 해제 → 자산 재평가) |
| **Value Chain 선행 배치** | 산업분석 첫 장에 자체 제작 밸류체인 다이어그램을 배치, 기업 위치를 즉각 표시 | SMIC JTC, STAR GaN |
| **과거 유사 사례 논증** | 리스크를 나열만 하지 않고, 과거 동일 사건 기업(관리종목, 구조조정)의 주가 궤적으로 반박 | SMIC JTC (국순당, 알톤스포츠 사례) |
| **지분구조 Timeline 도식화** | 복잡한 대주주/PE/콜옵션/Drag-along을 Timeline SVG로 시각화 | SMIC JTC (어펄마캐피탈) |
| **수수료/비용 내재화 정량 분석** | 중간 단계 제거(캡티브 브로커, 자체 유통망)로 인한 비용 절감을 건당 단가×물량으로 정량 산출 | YIG 키움증권 (캡티브 브로커 2bp=연 170억 절감) |
| **기술 로드맵 연동** | 주요 고객사/플랫폼의 기술 로드맵(Nvidia Hopper→Blackwell→Rubin 등)과 동사 제품 수요를 직접 연결 | S.T.A.R GaN반도체 |
| **규제/정책 실시간 이슈 반영** | 최신 규제 변화(벌금, 수출 제재, 우회 적발 등)를 보고서에 반영하여 시의성 확보 | S.T.A.R (TSMC 10억달러 벌금, CoAsia 우회 수출) |
| **IP 파생 수익화 모델** | 콘텐츠 IP의 지역별 수익화 모델(GEM, AVOD/SVOD, 토큰 등)을 개별 분석 | SMIC 애니플러스 (라프텔 GEM 모델, 동남아) |
| **작품/IP 패러디 소제목** | 분석 대상 IP의 용어/세계관을 섹션 제목에 차용하여 가독성+재미 ("성장의 호흡 제1의 형 「서사」") | SMIC 애니플러스 |

### 9-4. 89점 자동 달성 요건 (5개 영역 × 필수 조건)

**각 영역 18점 이상 = 총점 90점.** 아래 조건을 모두 충족해야 한다.

#### [논리 18점] 필수 조건
- counter_arg 3건+ (IP마다 1건, "시장의 우려 → 반박" 패턴)
- 독자적 분석 프레임 1개 (종목마다 고유한 분석 개념)
- 과거 사이클 Analogy 테이블 (유사 시점과 비교)
- 인과관계 3단+ 체인 (A→B→C→투자결론)
- Bear case를 IP 본문에서 선제 논파 (리스크 섹션이 아니라 IP에서!)
- 1차 데이터 1건+ (전문가 인터뷰/플랫폼 크롤링/커뮤니티 추적/공공데이터 중 택1)

#### [추정 18점] 필수 조건
- P×Q (또는 산업 특화 Bottom-up) 5개년, 사업부별 ASP/Q 각 추정 근거 400자+
- ASP 분해 테이블 (기초→MIX→가격→환율→최종) or 수주전환율 분해
- 원가 7항목+ Bottom-up (자재/인건비/감가/외주/전기광열/R&D/기타)
- 분기별 추정표 + 해설
- 3중 밸류에이션 (PER+PBR or EV/EBITDA+DCF) 크로스체크
- WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
- Football Field + DCF 민감도 히트맵
- "Why X? Why not Y?" 밸류에이션 방법론 선택/배제 근거 섹션 필수
- Implied PER sanity check (DCF 사용 시 터미널연도 내재 PER 합리성 검증)

#### [시각화 18점] 필수 조건
- SVG 50개+ (섹션당 최소 4개)
- MLA 밸류체인 5-Layer SVG (산업 밸류체인)
- DSA 시스템 아키텍처 SVG (핵심 논리 플로우)
- 산업 사이클 포지션 SVG (현재 위치 표시)
- 인터랙티브: expand_card 5+, sticky, progress, float-toc, page-break
- 반응형 3-breakpoint (1024/768/480px)
- hover 효과, tabular-nums

#### [서술력 18점] 필수 조건
- **마크다운 본문 75,000자+ (Phase 1에서 확보)**
- 산업 기초 설명 2,000자+ (비전공자도 이해 가능)
- 전문용어 첫 등장 시 정의
- 모든 차트/테이블 전후에 해설 문단 (pre: "왜 보는가", post: "핵심 시사점")
- 숫자에 맥락 부여 ("22.1조원 = GDP의 ~1%")
- 모든 분석 문단이 "그래서 투자자는"으로 귀결

#### [구조 18점] 필수 조건
- 11섹션 완비 (Appendix 테이블 16개)
- Key Chart 인트로 + 용어정리 12개+
- 도표번호 전수 + 출처 전수
- callout(KEY TAKEAWAY) 3개+ + insight-box 1개+
- 스크롤 UX 5종 (progress/toc/dots/back-top/page-break)
- 재무데이터 Excel 연동 (있는 경우 자동 Appendix)
- 용어 정리(Glossary) 테이블 10개+ 구현 (gen_glossary 헬퍼)
- Key Chart 인트로 2×2 그리드 구현 (gen_key_charts 헬퍼)

### 9-4b. HARD MINIMUM (이 기준 미달 시 빌드 실패 처리)

**현대건설 v1에서 발견된 문제**: 텍스트 33,205자(목표의 42%), 테이블 9개(목표의 25%), 섹션당 1,200자(목표 4,000자의 30%). 스킬 템플릿을 써도 **내용을 충분히 채우지 않으면** 빈약한 보고서가 나온다.

#### 정량 최소 기준 (빌드 함수에서 자동 검증)

| 항목 | 최소 기준 | 검증 방법 |
|------|----------|----------|
| **총 텍스트** | **60,000자 이상** | `len(text_only) >= 60000` |
| **섹션당 텍스트** | **3,000자 이상** (Appendix 제외) | 섹션별 측정 |
| SVG 차트 | 25개 이상 | `html.count('<svg ') >= 25` |
| 테이블 | 20개 이상 | `html.count('<table') >= 20` |
| 도표 번호 | 40개 이상 | — |
| 출처 | 40개 이상 | — |
| counter_arg | 3건 이상 (IP마다 1건) | `html.count('시장의 우려') >= 3` |
| Appendix 테이블 | 8개 이상 (IS/BS/CF/주당/Valuation/Peer/DCF/체크리스트) | — |

#### 섹션별 필수 구성 요소 (하나라도 빠지면 불완전)

```
[섹션1 기업개요] 최소 4,000자
□ 사업부별 매출 비중 도넛
□ 수주잔고/매출 추이 바 차트
□ MLA 밸류체인 5-Layer SVG
□ expand_card 3개+ (산업 기초, 사업부 상세, 역사)
□ 사업부 비교 테이블
□ KEY TAKEAWAY callout

[섹션2 산업분석] 최소 4,000자
□ 사이클 포지션 SVG
□ 시장 규모 추이 바 차트
□ 지역별/분야별 도넛
□ TOP 10 기업 테이블
□ 차트 전후 해설 문단

[섹션3 투자포인트①] 최소 3,000자
□ counter_arg 1건
□ DSA 시스템 아키텍처 SVG
□ 워터폴 or 타임라인 차트
□ KEY TAKEAWAY callout

[섹션4 투자포인트②] 최소 3,000자
□ counter_arg 1건
□ 지역/분야별 시각 다이어그램
□ 관련 데이터 차트 2개

[섹션5 투자포인트③] 최소 3,000자
□ counter_arg 1건
□ PER 밴드 차트
□ PBR 밴드 차트
□ insight-box

[섹션6 재무분석] 최소 4,000자
□ 매출/OPM 이중축 차트
□ 마진율 추이 라인
□ 현금흐름 그룹 바 or 테이블
□ 듀폰분해 테이블
□ DIO/DSO/DPO 테이블 (건설업이면 수주잔고/매출인식 테이블)
□ ROIC vs WACC 테이블
□ 재무 요약 테이블

[섹션7 Peer비교] 최소 2,500자
□ OPM vs PER 산점도
□ ~~레이더 차트~~ (v13 금지 — svg_grouped_bar 또는 svg_scatter로 대체)
□ Peer 비교 테이블

[섹션8 실적추정] 최소 4,000자
□ P×Q 사업부별 매출 추정 테이블
□ 분기별 추정 테이블
□ ASP 분해 테이블 (or 수주전환율 분해)
□ 매출원가 Bottom-up 분해 테이블
□ EPS 추이 바 차트
□ Bull/Base/Bear 시나리오
□ 연간 실적 추정 요약 테이블

[섹션9 밸류에이션] 최소 3,000자
□ WACC 산출 상세 테이블
□ Football Field SVG
□ DCF 민감도 히트맵
□ 밸류에이션 Summary 테이블
□ 워터폴 (확률 가중 목표주가)

[섹션10 리스크] 최소 3,000자
□ EPS 민감도 테이블
□ 리스크 매트릭스 버블 SVG
□ 모니터링 체크포인트 테이블
□ EPS 영향도 시각화 SVG

[섹션11 Appendix] 최소 5,000자
□ A-1: 포괄손익계산서 (7열: 2022A~2028E)
□ A-2: 재무상태표
□ A-3: 현금흐름표
□ A-4: 주당지표
□ A-5: 밸류에이션 Summary
□ A-6: DCF 민감도 매트릭스
□ A-7: Peer 상세 비교
□ A-8: 투자 체크리스트
```

#### 빌드 함수 자동 검증 코드

```python
# build() 함수 마지막에 반드시 포함
HARD_MIN = {
    # === v9 HARD MINIMUM (빌드 실패 시 자동 중단) ===
    'text_60k': (text_chars >= 60000, f'text {text_chars:,} < 60,000'),
    'svg_50': (svg_count >= 50, f'SVG {svg_count} < 50'),
    'tables_25': (table_count >= 25, f'tables {table_count} < 25'),
    'subheadings_20': (h2h3_count >= 20, f'h2/h3 {h2h3_count} < 20'),
    'counter_arg_3': (html.count('counter-arg') >= 3, 'counter_arg < 3'),
    'appendix_16': (html.count('Appendix A-') >= 16, 'Appendix < 16'),
    'glossary_10': (glossary_count >= 10, 'glossary terms < 10'),
    'compliance': ('Compliance Notice' in html, 'Compliance Notice 없음'),
    'ai_watermark': ('AI-Assisted' in html, 'AI 워터마크 없음'),
    'football_field': ('football' in html.lower() or 'Football' in html, 'Football Field 없음'),
    'sensitivity': ('sensitivity' in html.lower() or '민감도' in html, '민감도 히트맵 없음'),
    'dual_valuation': (valuation_method_count >= 2, f'Valuation 방법론 {valuation_method_count} < 2'),
    'source_coverage': (source_count / max(svg_count + table_count, 1) >= 0.9, f'출처 커버리지 {source_count}/{svg_count+table_count} < 90% (STAR급 목표)'),
    'no_prospect': (html.count('전망이다') + html.count('판단된다') + html.count('예상된다') <= 3, '추측체 3회 초과'),
    'paragraph_uniform': (para_std < 200, f'문단 길이 표준편차 {para_std:.0f} > 200'),
    'xlsx_exists': (xlsx_generated, '데이터 엑셀 미생성'),
    'main_idea': ('Main Idea' in html or 'main-idea' in html, 'Main Idea 구조도 없음'),
    'stock_analysis': ('주가분석' in html, '주가분석 섹션 없음'),
    'why_not_val': ('부적합' in html or 'Why not' in html, 'valuation exclusion rationale missing'),
}
fails = [msg for ok, msg in HARD_MIN.values() if not ok]
if fails:
    print('\\n!!! HARD MINIMUM FAILURES !!!')
    for f in fails:
        print(f'  FAIL: {f}')
    print('보고서 품질 미달 — 내용을 보강할 것.')
```

### 9-5. HTML 보고서 전체 체크리스트

빌드 후 반드시 확인:

```
[구조]
□ 커버: 투자의견/목표주가/IS 7열+/Key Metrics/Bull-Base-Bear
□ TOC: 앵커링크 (페이지번호 X)
□ Key Chart 인트로: 핵심 차트 4개 모아 1페이지
□ 용어 정리: 산업 특화 용어 10~15개 테이블
□ 전 섹션 sidebar-layout + 사이드 캡션(키워드+메시지)
□ 섹션 헤더: "Equity Research Report | 종목명 (코드)"

[분석 품질]
□ 산업분석: 시장 구조/동인/경쟁/전동화 등 기초부터 설명
□ 투자포인트: IP별 Bear case 선제 논파 포함
□ 과거 사이클 Analogy 테이블 포함
□ 독자적 분석 프레임 1개 이상

[추정 품질]
□ P×Q: 제품 단위까지 세분화, 5개년(2024A~2028E)
□ 매출원가: 항목별 Bottom-up 분해 (원가율 퉁치기 금지)
□ 비용추정: 판관비도 인건비/R&D/기타 분리
□ 분기별 추정표 포함
□ 운전자본: DIO/DSO/DPO/CCC

[밸류에이션]
□ 최소 2개 방법론 크로스체크
□ WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
□ Football Field 차트
□ DCF 민감도 매트릭스

[리스크]
□ EPS 민감도 정량화 (변수별 ±영향)
□ 리스크 매트릭스 (발생확률 × 영향도)
□ 모니터링 체크포인트 테이블

[시각화]
□ SVG 50개+, 테이블 25개+
□ 도표 번호 전수 ("도표 X-Y.")
□ 출처 전수 (chart-box 하단)
□ MLA 밸류체인 계층도 (Layer 1→5, ↓ 방향)
□ DSA 시너지 아키텍처 (입력→합산→결과)
□ 중복 차트 금지 (동일 데이터 2개 형식 이하)

[Appendix]
□ IS/BS/CF 5개년
□ 주당지표
□ Valuation Summary
□ DCF 민감도
□ Peer 상세
□ FCFF 상세
□ 투자 체크리스트
□ 추정 IS/BS/CF 확장 (통합 기준)
□ P×Q 5개년 확장
□ WACC 민감도
```

## 10. 시각화 고급 기법 (STAR/EIA/웹 리서치 종합)

### 10-1. 차트 내 콜아웃 박스 (STAR GaN 벤치마크)

차트 안에 빨간 테두리 박스나 화살표로 핵심 인사이트를 직접 삽입하는 패턴.
독자가 차트를 해석할 필요 없이 "이걸 봐라"를 명시.

```python
# SVG 차트 내 콜아웃 예시
svg += f'<rect x="..." y="..." width="120" height="30" rx="4" fill="none" stroke="#FF4D4D" stroke-width="1.5" stroke-dasharray="4"/>'
svg += f'<text x="..." y="..." fill="#FF4D4D" font-size="9" text-anchor="middle">핵심 인사이트</text>'
```

### 10-2. 주가 이벤트 주석 차트 (EIA 인텔리안 벤치마크)

주가 라인 차트 위에 주요 이벤트(수주 공시, 실적 발표, 합병 발표 등)를 화살표+텍스트로 직접 표기.
"왜 이 시점에 주가가 움직였는가"를 시각적으로 설명.

### 10-3. Sticky 헤더 (웹 리서치)

HTML 보고서에서 스크롤해도 종목명/목표가/투자의견이 항상 화면 상단에 노출.
```css
.sticky-header { position:sticky; top:0; z-index:100; background:var(--bg);
  padding:8px 20px; border-bottom:1px solid var(--border); }
```

### 10-4. 금융 테이블 국제 표준 (CFA + 웹 리서치)

- **음수 표기**: 괄호 `(1,234)` + 빨간색 (△ 기호도 OK)
- **세로선 없음**: 가로 구분선만 사용 (금융 보고서 표준)
- **합계/소계 행**: 상단 1px 실선 + 볼드
- **추정치 구분**: 연도에 "E" 접미사 (2026E), 컬럼 배경색 미세 차이
- **`font-variant-numeric: tabular-nums`** 전역 적용

### 10-6. 사이드 마진노트 패턴 (STAR/SMIC/EIA 공통)

모든 벤치마크 보고서의 공통 디자인 요소:
- 좌측 여백(페이지 폭의 ~20%)에 해당 단락의 **핵심 메시지 1줄**을 배치
- 바쁜 독자가 마진노트만 훑어도 전체 논지 파악 가능 (skim reading 최적화)
- HTML에서는 `sidebar-layout`의 `.sidebar-kw`에 키워드+수치 뿐 아니라 **핵심 메시지 문장**도 포함

### 10-7. 차트 디자인 금지 사항 (웹 리서치 종합)

- 3D 효과 절대 금지
- 불필요한 그라디언트/그림자 금지 (chart junk)
- 색상 12개 초과 금지 (6개 이하 권장)
- 순수 빨강-녹색 조합 금지 (색맹 대응 → 청-주황 권장)
- 범례를 차트 밖에 분리하지 말고 데이터 위에 직접 라벨링
- Y축 라벨(값) 누락 금지 — 그리드라인만 있으면 의미 없음

## 11. 전 항목 19점 달성 설계 (v6+ 자동화 패턴)

2026.03 벤치마크 평가(SMIC/YIG/STAR/EIA 6건 vs 우리 v5) 결과:
- 시각화 18점(1위), 구조 18점(공동1위) → 유지
- **논리 14점(꼴찌), 서술력 14점(꼴찌), 추정 16점** → 개선 필수

### 11-1. 논리/분석력 14→19: 반론 선제 논파 자동화

**문제**: Bear case를 리스크 섹션에 나열만 함. IP 본문에서 정면 반박 안 함.
**해결**: 매 투자포인트에 `counter_arg()` 블록 삽입.

```python
def counter_arg(concern, rebuttal):
    """반론 선제 논파 블록 (SMIC S-Oil 벤치마크)"""
    return f'''<div style="background:rgba(255,77,77,0.05);border-left:3px solid var(--red);padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0;">
<p style="font-size:13px;color:var(--red);font-weight:600;margin-bottom:6px;">시장의 우려</p>
<p style="font-size:13px;color:var(--text-sec);margin-bottom:8px;">{concern}</p>
<p style="font-size:13px;color:var(--green);font-weight:600;margin-bottom:6px;">반박</p>
<p style="font-size:13px;color:var(--text);margin:0;">{rebuttal}</p>
</div>'''
```

**필수 적용 위치** (매 IP에 최소 1개):

| 섹션 | 우려 | 반박 |
|------|------|------|
| IP1 시너지 | "합병 시너지 3,000억원은 과대 추정 아닌가? 과거 건설기계 합병에서 시너지 미달 사례가 많다" | "Komatsu-Joy Global(매출 대비 3.5%), Volvo-Terex(3~4%) 사례에서 동일 수준 실현. HD건설기계 3,000억원은 합산 매출의 3.6%로 업종 평균 범위 내" |
| IP2 업사이클 | "중국 부동산 침체가 장기화되면 글로벌 업사이클 자체가 무산되는 것 아닌가?" | "중국 비중 15%이며, 북미 IIJA+인도 Gati Shakti+중동 NEOM의 정부 주도 인프라 투자는 경기 독립적. 중국 제외 나머지 85% 지역의 성장률만으로도 +5% 달성 가능" |
| IP3 밸류에이션 | "합병 초기 PER 프리미엄이 과도하며, Korea Discount가 해소될 근거가 없다" | "합병 리스크 프리미엄은 시간 감소 특성. PMI 완료(2027)와 함께 자연 해소. MSCI 편입($4.9B > 기준 $3B)으로 패시브 자금 $300~500M 유입 기대" |

**논리 점수 올리는 추가 기법**:
- **독자적 분석 프레임**: 종목마다 1개 이상의 고유 개념 도입 (키움의 "키움 Multiplier"처럼)
  - 예: "시너지 실현률(SRR: Synergy Realization Rate)" — 분기마다 추적 가능한 지표
- **인과관계 체인**: 매 IP에서 "A이므로 B → B이므로 C → C이므로 D(투자결론)" 3단 이상 체인
- **정량적 반박**: "~가 우려되지만, 실제 영향은 EPS 기준 ±X원에 불과하다" 숫자로 반박

### 11-2. 추정/밸류에이션 16→19: ASP 근거 + 원가 분해 심화

**문제**: ASP 추정이 "MIX 개선" 한 줄. 원가 항목이 7개로 얕음.
**해결**: ASP 분해 테이블 + 원가 7항목+ 분해 (12항목 권장).

```python
# ASP 분해 테이블 (v6 필수)
table(
    ["ASP 변동 요인", "2025A", "영향(%)", "2026E ASP", "근거"],
    [
        ["기초 ASP", "1.75억", "—", "1.75억", "2025 실적 기준"],
        ["MIX 개선 (대형↑)", "—", "+1.7%", "+0.03억", "대형 비중 18%→20%, ASP 2배"],
        ["가격 인상", "—", "+1.1%", "+0.02억", "원자재 전가 + Tier4F 고사양"],
        ["환율 효과", "—", "+0.0%", "—", "1,350원 가정 (현행 유지)"],
        ["최종 ASP", "1.75억", "+2.9%", "1.80억", ""],
    ],
    highlight_rows={4}
)
```

**원가 7항목+ 분해 (필수, 12항목 권장)**:
1. 원재료비 (철강/유압/전장) — 매출원가의 60%
2. 인건비 (생산직) — 15%
3. 감가상각비 — 3.5%
4. 외주가공비 — 8%
5. 전기광열비 — 3%
6. 수선비 — 2%
7. 경상연구개발비 — 2.5%
8. 포장운반비 — 1.5%
9. 보험료 — 0.8%
10. 임차료 — 0.7%
11. 소모품비 — 1.5%
12. 기타 — 1.5%

각 항목에 YoY 변동률 + 변동 근거 1문장 필수.

### 11-3. 서술력 14→19: 차트 전후 해설 자동화

**문제**: 차트가 연속 나열되고 해설 문단이 빠진 구간 다수.
**해결**: `chart_with_context()` 래퍼로 강제 해설 삽입.

```python
def chart_with_context(pre_text, chart_html, post_text):
    """차트 전후 해설 문단 강제 삽입 (SMIC 패턴)"""
    h = f'<p style="font-size:14px;line-height:1.8;color:var(--text);margin-bottom:12px;">{pre_text}</p>\n'
    h += chart_html
    h += f'<p style="font-size:14px;line-height:1.8;color:var(--text);margin:12px 0;">{post_text}</p>\n'
    return h
```

**필수 규칙**:
- `chart_with_context(pre, chart, post)` 없이 `svg_*()` 직접 호출 금지
- 단, `<div class="chart-pair">` 안의 2열 차트는 pair 전후로 1세트만 적용 가능
- pre_text: "이 데이터를 왜 봐야 하는가" (최소 3문장, 200자)
- post_text: "핵심 시사점 + 그래서 투자자는 어떻게" (최소 3문장, 200자)

**서술 밀도 체크 자동화**:
```python
# build 함수 마지막에 자동 검증
sections = html.split('class="section"')
for i, sec in enumerate(sections[1:], 1):
    charts = sec.count('<svg ')
    texts = len(re.findall(r'<p[^>]*>(.{100,}?)</p>', sec))
    if charts > 0 and texts / charts < 2:
        print(f"  WARNING: sec{i} 차트당 해설 문단 {texts/charts:.1f}개 (최소 2개 필요)")
```

### 11-4. 시각화 18→19: 미세 개선

이미 1위지만 19점을 위해:
- **차트 내 콜아웃 박스**: 핵심 데이터 포인트에 빨간 점선 사각형 + 인사이트 텍스트 (STAR GaN 벤치마크)
- **annotated 주가 차트**: 주요 이벤트(합병 발표, 실적 발표)를 주가 선 위에 직접 표기 (EIA 벤치마크)
- **바 차트 width 통일**: 모든 바 차트에서 bar_w를 동일하게 고정

### 11-5. v6 빌드 체크리스트 (전 항목 19점 기준)

```
[논리 19점]
□ 매 IP에 counter_arg() 반론 선제 논파 1개+
□ 독자적 분석 프레임 1개 (SRR, Multiplier 등)
□ 인과관계 3단 체인 (A→B→C→투자결론)
□ 정량적 반박 ("EPS ±X원에 불과")

[추정 19점]
□ ASP 분해 테이블 (기초+MIX+가격+환율=최종)
□ 원가 7항목+ Bottom-up (각 항목 YoY 근거, 12항목 권장)
□ 비용추정 독립 섹션 (판관비도 인건비/R&D/수수료/기타 분리)
□ P×Q 5개년, 분기별 추정표

[시각화 19점]
□ 차트 내 콜아웃 박스 (핵심 데이터에 빨간 점선 사각형)
□ annotated 주가 차트 (이벤트 주석)
□ 바 차트 width 통일
□ 기존 v5 요소 전부 유지

[서술력 19점]
□ 매 차트/테이블에 chart_with_context(pre, chart, post)
□ pre: "왜 보는가" 3문장 200자+
□ post: "핵심 시사점" 3문장 200자+
□ 서술 밀도 자동 검증 (차트당 해설 2문단 이상)

[구조 19점]
□ 11개 섹션 (v9 확정, 비용추정은 실적추정에 포함)
□ 기존 v5 요소 전부 유지
□ 실적추정 섹션에 원가 7항목+ + 판관비 분리
```

## 12. 스크롤 피로 해소 UX (v7+ 필수)

HTML 보고서가 250KB+로 길어지면 스크롤 피로가 심각. 5가지 UX 요소를 필수 적용.

### 12-1. 읽기 진행률 바
- 최상단 고정(position:fixed), 퍼플 그라데이션, 3px 높이
- `requestAnimationFrame` + `passive:true`로 성능 최적화

### 12-2. Floating Sticky TOC
- 우측 고정(right:16px, top:80px), 반투명 배경, backdrop-filter:blur
- `IntersectionObserver` 또는 scroll handler로 현재 섹션 하이라이트(.active)
- 1200px 미만에서 자동 숨김(@media)

### 12-3. 시각적 페이지 구분선
- 대섹션 전환(기업분석→재무, 추정→밸류에이션, 리스크→Appendix)에 배치
- 그라데이션 수평선 + 중앙에 "FINANCIAL ANALYSIS" 등 영문 라벨
- `.page-break` 클래스, height:60px, margin:48px 0

### 12-4. Back to Top 버튼
- 우하단 고정, 퍼플 원형, scrollY > 400에서 표시
- hover 시 배경색 반전, smooth scroll

### 12-5. 섹션 도트 인디케이터
- 좌측 고정(left:12px), 세로 나열, 현재 섹션 활성화(scale 1.6 + 퍼플)
- 클릭 시 해당 섹션으로 smooth scroll
- 1200px 미만에서 자동 숨김

### 12-6. 성능 규칙
```javascript
// 반드시 requestAnimationFrame + passive 사용
let ticking = false;
window.addEventListener('scroll', () => {
  if(!ticking){
    requestAnimationFrame(() => { updateUI(); ticking = false; });
    ticking = true;
  }
}, {passive:true});
```

## 13. SMIC 수준 자동 생성 메커니즘 (종합)

다음 종목 보고서 빌드 시 자동으로 89점+가 나오는 구조:

### 13-1. 빌드 파이프라인
```
1. build_vN.py 복사 (헬퍼 함수 재사용)
2. 종목별 데이터 교체 (gen_cover ~ gen_section11)
3. 필수 체크:
   □ counter_arg() 3건+ (IP마다 1건)
   □ ASP 분해 테이블 (기초→MIX→가격→환율→최종)
   □ 매출원가 Bottom-up 7항목+
   □ 차트 전후 해설 문단 6건+
   □ Key Chart 인트로 + 용어정리
   □ 과거 사이클 Analogy 테이블
   □ MLA + DSA 다이어그램
   □ 스크롤 UX 5종 (진행률바/TOC/구분선/Back to Top/도트)
4. 빌드 → 자동 검증 → 문제 있으면 수정 후 재빌드
```

### 13-2. 자동 검증 항목 (build 함수에 포함)
```python
# 빌드 후 자동 체크
checks = {
    'counter_arg': html.count('시장의 우려') >= 3,
    'chart_context': len(re.findall(r'margin:12px 0', html)) >= 6,
    'asp_decomp': 'ASP 변동 요인' in html,
    'mla_diagram': '밸류체인 계층도' in html,
    'dsa_diagram': '시스템 아키텍처' in html,
    'key_charts': 'Key Charts' in html,
    'glossary': '용어 정리' in html,
    'cycle_analogy': '과거 사이클' in html,
    'progress_bar': 'reading-progress' in html,
    'float_toc': 'float-toc' in html,
    'page_breaks': 'page-break' in html,
    'text_75k': text_chars >= 75000,
    'svg_50': svg_count >= 50,
    'tables_25': table_count >= 25,
}
for name, passed in checks.items():
    status = 'OK' if passed else 'FAIL'
    print(f'  [{status}] {name}')
```

### 13-3. 우리만의 강점 (절대 포기하지 않을 것)
1. **인터랙티브 HTML** — 정적 PDF 학회 대비 압도적 시각 경험
2. **다크 테마 퍼플** — 브랜드 아이덴티티
3. **hover/sticky/progress** — 읽기 경험 최적화
4. **MLA/DSA 인라인 SVG** — 아키텍처 시각화
5. **16종 SVG 헬퍼** — 어떤 데이터든 즉시 시각화 가능
6. **인터랙티브 요소** — PDF 학회 절대 불가. 클릭/호버/탭 전환

## 13-4. 인터랙티브 요소 (HTML 전용 킬러 피처)

PDF 학회들이 절대 따라올 수 없는 우리만의 무기. 3가지 인터랙티브 헬퍼:

### expand_card(title, meta, content)
클릭하면 펼쳐지는 MLA/DSA 스타일 카드. 긴 상세 정보를 접어두고 필요시 펼침.
- **사용처**: 생산거점 상세, Appendix 재무제표, 사업부 심층 분석
- **효과**: 스크롤 피로 감소 + 정보 계층화
```python
h += expand_card("울산 공장 (본사)", "대형 굴착기·휠로더 | 연 12,000대",
    '<p>상세 설명...</p>')
```

### scenario_tabs(bull, base, bear)
Bull/Base/Bear 시나리오를 탭으로 전환. 3개 시나리오를 같은 공간에 표시.
- **사용처**: 섹션8 실적추정, 섹션9 밸류에이션
```python
h += scenario_tabs(bull_html, base_html, bear_html)
```

### data_tip(text, tip)
마우스 올리면 상세 설명 팝업. 전문 용어나 핵심 수치에 적용.
- **사용처**: 본문 내 전문용어, 핵심 가정 수치
```python
f'WACC {data_tip("10.0%", "Ke 10.1% × 54% + Kd 3.4% × 46% + 합병리스크 3%p")}를 적용'
```

### 인터랙티브 적용 가이드
| 요소 | 위치 | 용도 |
|------|------|------|
| expand_card × 4~6 | 섹션1 생산거점, 섹션11 Appendix | 상세 정보 접기 |
| scenario_tabs × 1 | 섹션8 Bull/Base/Bear | 시나리오 전환 |
| data_tip × 10+ | 전 섹션 핵심 수치 | 가정 근거 표시 |
| hover 효과 | 모든 SVG rect/circle | 데이터 강조 |
| sticky 헤더 | 전체 | 종목/투자의견 상시 노출 |
| progress bar | 전체 | 읽기 진행률 |
| float TOC | 우측 | 현재 섹션 추적 |
| section dots | 좌측 | 빠른 섹션 이동 |

## 14. Builder-Evaluator 패턴 (Anthropic Labs GAN 영감)

Anthropic Labs의 "만드는 Claude + 심사하는 Claude" 패턴을 보고서 빌드에 적용.
단일 에이전트의 한계: (1) 컨텍스트 불안감으로 후반 품질 저하, (2) 자기 작품에 대한 편향.

### 14-1. 3-Agent 파이프라인

```
Phase 1: Planner (에이전트 1)
- 종목 분석 프레임 설계
- IP 3개 + Bear case 3개 사전 구조화
- P×Q 사업부 분류, ASP/Q 추정 방향 설정
- 독자적 분석 프레임 1개 제안

Phase 2: Builder (에이전트 2)
- build_template.py 복사 → 종목별 데이터 교체
- 섹션 1~11 본문 작성
- SVG 차트 + 테이블 생성
- counter_arg 3건+, chart_with_context 적용

Phase 3: Evaluator (에이전트 3) ← 핵심
- 생성된 HTML을 직접 읽고 심사
- 5개 항목(논리/추정/시각화/서술력/구조) × 20점 채점
- "차트당 해설 문단 수" 자동 계산
- counter_arg 존재 여부 확인
- 구체적 개선 지시 → Builder에게 전달
- 85점 이상 될 때까지 반복
```

### 14-2. Evaluator 프롬프트 (서브에이전트용)

```
생성된 HTML 보고서를 읽고 5개 항목을 20점 만점으로 채점하라.
SMIC S-Oil(89점)을 기준으로 극도로 냉정하게 평가.

[논리] counter_arg 3건 이상? 독자적 프레임? 인과 3단 체인?
[추정] ASP 분해 테이블? 원가 7항목+? P×Q 5개년? 분기별?
[시각화] SVG 50+? 도표번호 전수? MLA/DSA? hover/sticky?
[서술력] 차트당 해설 2문단? 공허 문장 0? 실증적 근거?
[구조] 11섹션? Appendix A-1~16? 리스크 독립? Key Chart? Main Idea 구조도? 주가분석?

85점 미만이면 구체적 개선 지시를 3줄 이내로 제시.
```

### 14-3. Claude Code 실행 패턴

```python
# 실제 사용 시 (Claude Code에서)
# Phase 1: Plan
plan_agent = Agent(prompt="종목 분석 프레임 설계...")

# Phase 2: Build
build_agent = Agent(prompt="build_template.py 기반 보고서 생성...")

# Phase 3: Evaluate
eval_agent = Agent(prompt="생성된 HTML 심사, 85점 이상까지 반복...")

# Phase 4: Fix (Evaluator 피드백 기반)
fix_agent = Agent(prompt="Evaluator 지적사항 수정...")
```

## 15. 빌드 템플릿 (build_template.py)

`~/.claude/skills/cufa-equity-report/build_template.py`

종목 교체 시 수정 포인트:
1. `gen_cover()` — 종목명, IS 데이터, 사이드바
2. `gen_toc()` — 섹션 제목
3. `gen_key_charts()` — 핵심 수치 4개
4. `gen_glossary()` — 산업 용어
5. `gen_section1~11()` — 본문 전체
6. Sticky bar — 종목명/목표가/투자의견
7. Float TOC — 섹션 목록
8. `build()` output 경로

헬퍼 함수(svg_*, table, counter_arg, add_source, CSS, JS)는 **수정 불필요** — 그대로 재사용.

## 16. 디자인 안티패턴 금지 (바이브코딩 교훈)

AI 생성 보고서가 "AI가 만든 티"가 나지 않도록:

### 16-1. 금지 목록
- Inter 폰트 단독 사용 금지 → Noto Sans KR + 커스텀 페어링
- 뻔한 파란 그라데이션 금지 → 퍼플(#7C6AF7) 시그니처
- 둥근 카드 나열 금지 → 아키텍처형 구조 (MLA/DSA)
- 3D/글로우/네온 효과 금지
- "모던하고 깔끔한" 같은 모호한 지시 금지 → 구체적 레퍼런스 첨부
- Lucide 아이콘 디폴트 금지 → 텍스트 기반 또는 커스텀 SVG

### 16-2. 반드시 할 것
- **디자인 시스템 먼저**: 색상/폰트/간격 규칙을 CSS 변수로 정의 후 빌드 시작
- **레퍼런스 스크린샷**: SMIC S-Oil PDF의 특정 페이지를 레퍼런스로 제공
- **일관성 우선**: 페이지 간 스타일 통일이 독창성보다 중요
- **데이터 밀도**: 여백 남용 = 실패. 모든 공간에 정보를 채울 것

### 16-3. Nexus MCP 데이터 파이프라인 (실데이터 자동 수집)

보고서 작성 시 mock 데이터 대신 Nexus MCP로 실데이터를 자동 수집한다.
131개 도구 중 보고서에 필요한 핵심 도구:

```bash
# MCP 연결 (최초 1회)
claude mcp add nexus-finance --transport http http://62.171.141.206/mcp
```

| 데이터 | MCP 도구 | 사용 예시 |
|--------|---------|----------|
| 재무제표 (IS/BS/CF) | `dart_financial_statements` | "HD건설기계 재무제표 5개년" |
| 주가 데이터 | `stocks_market_overview` | "HD건설기계 주가 추이" |
| Peer 재무 | `dart_financial_statements` | "Caterpillar, Komatsu 재무 비교" |
| 거시경제 | `ecos_search` | "한국은행 기준금리, GDP 성장률" |
| 환율 | `ecos_get_exchange_rate` | "원/달러 환율 추이" |
| 원자재 | `crypto_*` 또는 외부 | "철강 가격 추이" |
| 산업 통계 | `rone_*` | "건설투자 추이" |

**빌드 파이프라인에 통합:**
```
Phase 0: Data Collection (Nexus MCP)
  → DART 재무제표 → P×Q 기초 데이터
  → pykrx 주가 → PER/PBR 밴드
  → ECOS 매크로 → 산업 분석 배경
Phase 1: Plan → Phase 2: Build → Phase 3: Evaluate
```

찬희님이 MCP를 확장하면 추가 데이터 소스(Bloomberg, 관세청, 산업통상자원부 등)도 자동 수집 가능.
**핵심: mock 데이터 절대 금지 → MCP에서 못 가져온 건 빈칸으로 두고, 찬희님에게 수동 입력 요청.**

- **멀티플 표기 규칙**: PER/PBR/EV-EBITDA에 반드시 기준 시점 명시
  - Forward: `Fwd PER 13.85배` 또는 `PER(12MF)`
  - Trailing: `PER(T) 25.20배`
  - 추정 기반: `2026E PER 14.8배`
  - Target: `Target PER 17.8배`
  - "PER 14배"처럼 기준 없이 쓰는 것 금지
- **산업별 미니멀 SVG 심볼**: `cufa-diagram` 스킬의 심볼 라이브러리 활용
  - 각 종목 보고서마다 해당 산업 심볼 4~6개를 SVG로 제작
  - MLA 다이어그램·섹션 제목·테이블·사이드바에 인라인 삽입
  - "글만 있는 보고서"에서 "보는 보고서"로 전환

## 17. 시스템 기반 보고서 생성 원칙 (X 글쓰기 시스템 + 바이브코딩 교훈)

### 17-1. 80/20 시스템 원칙
- **80%는 시스템이 잡아준다**: 구조, 문체, 포맷, 도표번호, 출처, sidebar, CSS — build_template.py가 자동 처리
- **20%는 사람이 다듬는다**: 투자 논리의 핵심, Bear case 반박의 설득력, 종목 특화 인사이트
- "매번 처음부터 쓰는 게 아니라, 시스템 위에서 쓴다"
- 반복 판단(구조/포맷/키워드)을 시스템에 맡기고, 소재 선택과 최종 다듬기에 집중

### 17-2. 피드백 루프로 시스템 진화
- 보고서 작성할 때마다 불편한 점 → 스킬에 규칙 추가
- "이건 매번 반복하는 지시인데?" → 헬퍼 함수로 자동화
- 예: 차트 해설이 빠짐 → `chart_with_context()` 함수화
- 예: 반론 논파 빠짐 → `counter_arg()` 함수화
- 예: 멀티플 기준 시점 누락 → 표기 규칙 추가

### 17-3. 디자인 시스템 우선 (바이브코딩 핵심)
- **코드 전에 디자인 시스템 정의**: CSS 변수(:root), 색상 팔레트, 폰트, 간격 규칙
- **레퍼런스 스크린샷 제공**: SMIC/YIG 보고서 특정 페이지를 시각적 참고로
- **모방 > 상상**: AI에게 "깔끔하게"라고 말하지 말고, 깔끔한 게 뭔지 보여줄 것
- **일관성 > 독창성**: 페이지 간 스타일 통일이 최우선
- **AI 생성 티 제거**: Inter 폰트 단독 X, Lucide 아이콘 X, 뻔한 파란 그라데이션 X

### 17-4. 재무데이터 Excel → Appendix 자동 생성 파이프라인

**핵심**: 보고서 작성 전에 항상 재무데이터를 엑셀(`.xlsx`)로 정리한다. 이 엑셀을 읽어서 Appendix 테이블을 자동 생성하면 수작업 ZERO.

#### 엑셀 표준 시트 구조
```
{종목명}_재무데이터.xlsx
├── Sheet1: IS (포괄손익계산서) — 매출/원가/GPM/판관비/영업이익/OPM/순이익/EPS (7열: 2022A~2028E)
├── Sheet2: BS (재무상태표) — 유동자산/비유동/총자산/유동부채/비유동/총부채/자기자본/부채비율
├── Sheet3: CF (현금흐름표) — 영업CF/투자CF/재무CF/FCF
├── Sheet4: Per-Share (주당지표) — EPS/BPS/DPS/PER/PBR/배당수익률
├── Sheet5: Peer (피어비교) — 시총/PER/PBR/OPM/ROE/배당/해외비중
├── Sheet6: Valuation — PER방법/PBR방법/DCF/WACC파라미터
└── Sheet7: PxQ (사업부별) — ASP/Q/매출/YoY (5개년)
```

#### 자동 생성 코드 패턴
```python
import openpyxl

def load_financial_data(xlsx_path):
    """엑셀에서 재무데이터를 읽어 dict로 반환"""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    data = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        headers = [cell.value for cell in ws[1]]
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            rows.append(list(row))
        data[sheet_name] = {'headers': headers, 'rows': rows}
    return data

def gen_appendix_from_xlsx(xlsx_path):
    """엑셀 데이터로 Appendix HTML 자동 생성"""
    data = load_financial_data(xlsx_path)
    h = '<div class="appendix">\n'

    sheet_titles = {
        'IS': 'A-1. 포괄손익계산서 (억원)',
        'BS': 'A-2. 재무상태표 (억원)',
        'CF': 'A-3. 현금흐름표 (억원)',
        'Per-Share': 'A-4. 주당지표',
        'Peer': 'A-5. Peer 상세 비교',
        'Valuation': 'A-6. 밸류에이션 Summary',
        'PxQ': 'A-7. P×Q 워크시트',
    }

    for sheet_name, title in sheet_titles.items():
        if sheet_name in data:
            d = data[sheet_name]
            h += f'<p style="font-size:13px;color:var(--text-sec);margin:24px 0 12px;">'
            h += f'<strong style="color:var(--purple-light);">{title}</strong></p>\n'
            h += table(
                [str(x) for x in d['headers']],
                [[str(cell) if cell is not None else '' for cell in row] for row in d['rows']],
                src="DART, CUFA 추정"
            )
    h += '</div>\n'
    return h
```

#### 사용 방법
```python
# build 함수에서
xlsx_path = r"C:\Users\lch68\Desktop\{종목명}_재무데이터.xlsx"
if os.path.exists(xlsx_path):
    h += gen_appendix_from_xlsx(xlsx_path)
else:
    h += gen_section11()  # 수동 Appendix 폴백
```

**워크플로우**: 재무데이터 엑셀 정리(찬희님) → build 스크립트가 자동으로 읽어서 Appendix 생성 → 수작업 ZERO

### 17-5. 디자인 도구 체인
- **Stitch by Google** (stitch.withgoogle.com): 음성 대화로 UI 디자인. 한국어 지원. Figma/Google AI Studio로 export 가능
  - 보고서 레이아웃 프로토타입에 활용 → 스크린샷 찍어서 AI에게 "이 스타일을 따라줘"
  - MCP 지원으로 실시간 배포 가능
- **Excalidraw**: 와이어프레임 스케치 → AI에게 구조 전달
- **Dribbble/Mobbin**: 레퍼런스 스크린샷 수집
- **Google Fonts**: Noto Sans KR + 개성 있는 display 폰트 조합


## 18. 밸류에이션 방법론 확장 (14개 보고서 기반)

### 18-1. 방법론 8종 매트릭스

| 방법론 | 언제 사용 | 언제 부적합 | 벤치마크 |
|--------|----------|------------|---------|
| Historical PER | 안정적 이익, 비교 가능한 과거 존재 | 적자 기업, 사이클 저점 | SMIC 파마리서치, Sensient |
| Historical PBR | 자산 중심, 금융업 | 자산 경량, 고성장 | YIG 심텍, 키움증권 |
| EV/EBITDA | 자본집약, 국가 간 비교 | EBITDA 음수, 규제 산업 | SMIC 두산 (SOTP 내) |
| DCF | 장기 성장, Peer 부재 | 짧은 영업 이력, 변동성 CF | SMIC 로보티즈, 코오롱티슈진 |
| RIM (초과이익모형) | 금융업, 안정적 BPS 성장 | 자본 변동성 큰 기업, 적자 | YIG 키움증권 |
| rNPV | 바이오 파이프라인 기업 | 비제약 기업 | SMIC 알지노믹스 |
| SOTP | 다각화 지주사, 복합 사업 | 단일 사업 | SMIC 두산, 풍산 |
| Historical Peer (과거 시점) | 현재 Peer 부적합, 과거 유사 상황 존재 | 과거 아날로그 없음 | SMIC 애니플러스 |

### 18-2. "Why X? Why not Y?" 템플릿

모든 밸류에이션 섹션에 반드시 포함해야 하는 방법론 선택/배제 근거 블록. SMIC 9건 전부 이 패턴을 따름.

```python
def valuation_rationale(chosen, chosen_reason, excluded_list):
    """밸류에이션 방법론 선택/배제 근거 블록 (SMIC 필수 패턴)

    Args:
        chosen: 선택한 방법론명 (str)
        chosen_reason: 선택 근거 3문장 (str)
        excluded_list: [(방법론명, 부적합 사유), ...] 2개+

    Examples:
        valuation_rationale(
            "DCF",
            "동사의 내재가치를 평가하는 방법으로 절대가치평가법인 DCF를 선택하였다. "
            "Historical 멀티플은 지속된 적자로 적합한 레코드가 부족하며, "
            "현재 시장이 동사에 기대하는 폭발적 성장을 담을 수 있는 유사한 과거 상황이 없다.",
            [
                ("Historical PER", "지속적 적자로 과거 PER 레코드 부적합"),
                ("Peer 멀티플", "상장된 유사 기업 부재, 글로벌 Peer도 사업 구조 상이"),
            ]
        )
    """
    h = '<div style="background:rgba(124,106,247,0.05);border-left:3px solid var(--purple);padding:16px;margin:20px 0;border-radius:0 4px 4px 0;">\n'
    h += f'<p style="color:var(--purple-light);font-size:14px;font-weight:700;margin-bottom:8px;">선택 방법론: {chosen}</p>\n'
    h += f'<p style="color:var(--text);font-size:13px;line-height:1.7;margin-bottom:12px;">{chosen_reason}</p>\n'
    h += '<div style="border-top:1px solid var(--border);padding-top:12px;">\n'
    for method, reason in excluded_list:
        h += f'<p style="color:var(--text-sec);font-size:13px;margin:4px 0;">✕ <strong>{method}</strong> 부적합: {reason}</p>\n'
    h += '</div></div>\n'
    return h
```

### 18-3. Implied PER Sanity Check

DCF로 목표주가를 산출한 경우, 터미널연도의 Implied PER을 역산하여 목표가의 합리성을 검증한다.

```
Implied PER = 목표주가 ÷ 터미널연도 EPS
```

판단 기준:
- Implied PER < 15x (터미널연도): 보수적 — 추가 상승 여력 존재
- Implied PER 15~30x: 합리적 범위
- Implied PER 30~40x: 공격적 — 고성장 전제 필요, 근거 보강
- Implied PER > 40x: Red Flag — 성장 가정 재검토 필수

벤치마크: SMIC 로보티즈 (Implied PER 25.39x@30E, 9.37x@34E → 10년 뒤 합리적)

```python
def implied_per_check(target_price, terminal_eps, terminal_year):
    """Implied PER sanity check (DCF 필수 동반)"""
    implied = target_price / terminal_eps if terminal_eps > 0 else float('inf')
    flag = '합리적' if implied < 30 else ('공격적' if implied < 40 else 'Red Flag')
    return f'''<div style="background:var(--surface2);padding:12px 16px;margin:12px 0;border-radius:4px;">
    <p style="font-size:13px;color:var(--text-sec);">Implied PER Sanity Check ({terminal_year}E)</p>
    <p style="font-size:15px;color:var(--text);font-weight:600;">
      목표주가 {target_price:,.0f}원 ÷ {terminal_year}E EPS {terminal_eps:,.0f}원 = <span style="color:{'var(--green)' if implied < 30 else 'var(--red)'};">{implied:.1f}x</span> ({flag})
    </p></div>'''
```

### 18-4. RIM (초과이익모형) 구현 패턴

YIG 키움증권이 PBR 밸류에이션의 보조 검증으로 사용. 금융업 종목에서 특히 유효.

```
V₀ = BPS₀ + Σ(RI_t / (1+COE)^t) + TV
RI_t = (ROE_t - COE) × BPS_{t-1}
TV = RI_n × (1+g) / (COE - g) / (1+COE)^n
```

파라미터:
- COE (Cost of Equity): CAPM = Rf + β × MRP
  - YIG 키움증권: COE 12.12% (Rf 3.186%, β 1.79, MRP 4.99%)
- TGR (Terminal Growth Rate): 보수적 0% 권장 (YIG 키움증권 사례)

```python
def rim_valuation(bps_0, roe_forecast, coe, tgr, years=5):
    """RIM (Residual Income Model) 밸류에이션
    roe_forecast: [ROE_1, ROE_2, ..., ROE_n] (소수점, e.g., 0.16)
    coe: Cost of Equity (소수점, e.g., 0.12)
    tgr: Terminal Growth Rate (소수점, e.g., 0.0)
    """
    bps = bps_0
    ri_pv_sum = 0
    for t, roe in enumerate(roe_forecast, 1):
        ri = (roe - coe) * bps
        ri_pv = ri / (1 + coe) ** t
        ri_pv_sum += ri_pv
        bps = bps * (1 + roe)  # retained earnings
    # Terminal Value
    ri_n = (roe_forecast[-1] - coe) * bps
    tv = ri_n * (1 + tgr) / (coe - tgr) / (1 + coe) ** len(roe_forecast) if coe > tgr else 0
    intrinsic = bps_0 + ri_pv_sum + tv
    return intrinsic
```

### 18-5. SOTP (Sum of Parts) 구현 패턴

SMIC 두산, 풍산에서 사용. 다각화 지주사/복합기업의 표준 밸류에이션.

```
NAV = Σ(사업부_i × EV/EBITDA_i) + 비영업자산 - IBD
주당 NAV = NAV / 유통주식수
목표주가 = 주당 NAV × (1 - 지주사 할인율)
```

SOTP 테이블 패턴:
```python
table(
    ["사업부", "EBITDA(E)", "적용 배수", "사업가치", "비중", "근거"],
    [
        ["굴착기", "5,200억", "8.5x", "44,200억", "52%", "Caterpillar 8.2x, Komatsu 9.1x 평균"],
        ["엔진", "1,800억", "7.0x", "12,600억", "15%", "Cummins 7.3x 참조"],
        ...
        ["합계", "—", "—", "85,000억", "100%", ""],
        ["(+) 비영업자산", "", "", "2,500억", "", "토지 공정가치"],
        ["(-) IBD", "", "", "12,000억", "", ""],
        ["NAV", "", "", "75,500억", "", ""],
    ],
    highlight_rows={-3, -1}
)
```


## 19. 1차 데이터 수집 가이드 (SMIC 최대 차별점)

SMIC 파마리서치의 독보적 강점 = 1차 데이터 수집. 이를 체계화하여 매 보고서에 최소 1건 포함.

### 19-1. 전문가 인터뷰 프로토콜

**사전 준비**:
- 질문 5개 이상 구조화 (투자포인트 검증용)
- 정량적 답변을 유도하는 질문 설계 ("연간 몇 건?", "비중이 몇 %?")
- 인터뷰이의 전문 분야와 경력 확인

**인터뷰 진행**:
- 녹취 동의 확보 → 전문(transcript) Appendix 수록
- 핵심 인용문은 본문 IP에서 직접 인용 ("현직 의사 A씨에 따르면...")

**Appendix 포맷**:
```python
expand_card(
    "전문가 인터뷰 #1 — 피부과 전문의 (경력 12년)",
    "인터뷰일: 2026.03.15 | 소속: 서울 강남구 소재 피부과",
    """<p><strong>Q1. 리쥬란 시술 수요 변화는?</strong></p>
    <p>A1. "23년 대비 25년 시술 건수가 약 30% 증가했다. 특히 중국인 환자 비중이..."</p>
    ..."""
)
```

벤치마크: SMIC 파마리서치 — 현직 피부과 의사/의료인력 9명 직접 인터뷰 전문 수록

### 19-2. 플랫폼 데이터 크롤링

| 플랫폼 | 데이터 유형 | 활용 예시 | 출처 표기법 |
|--------|------------|----------|-----------|
| 강남언니 | 시술 가격 | ASP 역산 (중위값/평균) | "강남언니 N건 시술가격 크롤링 기준 (2026.03)" |
| 네이버 쇼핑 | 제품 가격·판매량 | 국내 소비자 가격 추이 | "네이버 쇼핑 검색 기준" |
| Amazon | 리뷰 수·가격 | 해외 시장 침투도 | "Amazon.com 제품 리뷰 N건 기준" |
| App Store/Play Store | 앱 순위·리뷰 | 플랫폼 성장세 | "App Annie / Sensor Tower" |
| Kobis | 영화 관객수 | IP 매출 추정 | "영화진흥위원회 통합전산망" |

핵심 원칙: **크롤링 데이터는 반드시 수집 건수·일자·방법론을 명시.** "168건 크롤링"처럼 정량적으로.

**1차 가격조사 상세 프로토콜 (v9, SMIC 파마리서치 벤치마크)**:
- **최소 30건** 이상 개별 가격 수집 (이상치 제거 후 중위값/평균/분포 산출)
- 지역별×채널별 분류: 서울 강남(220K) vs 지방(110K) vs 해외(LaserAway 가격대)
- 수집 결과를 **Appendix 테이블로 전수 공개** (출처: 플랫폼명, 수집일)
- ASP 추정에 직접 연결: "30병원 평균 128,042원/cc → 연간 시술 건수 × ASP = 매출"

### 19-2b. 정성→정량 변환 방법론 (v9, SMIC 파마리서치 패턴)

커뮤니티/트렌드 데이터를 정량 KPI로 변환하는 공식:

```
수요 트렌드 지수 = W₁ × (커뮤니티 언급량 정규화) + W₂ × (검색트렌드 정규화)

예시 (SMIC 파마리서치):
  여우야 카페 월 게시글 856→1,134건 (가중치 W₁=75.9%)
  네이버 트렌드 지수 79.97→67.56 (가중치 W₂=39.8%)
  → 가중평균 = 856/1134 × 0.759 + 67.56/100 × 0.398 = 63.9%
```

**가중치 산정 근거 기록 필수**:
- W₁이 높은 이유: "국내 최대 미용 커뮤니티, 실제 수요층(MZ세대 여성)이 집중"
- W₂가 보조인 이유: "AI 알고리즘 특성상 종합지수이므로 특정 수요층 반영 약함"
- 가중치 산출 과정을 **Appendix에 반드시 기록**

**활용**: 매출추정의 Q(수량) 가정에 직접 연결. "트렌드 지수 +20%p → 시술 건수 +15% 가정"

### 19-3. 커뮤니티/소셜 시그널 추적

| 시그널 | 추적 방법 | 활용 | 벤치마크 |
|--------|----------|------|---------|
| 카페 게시글 수 | 월별 게시글 카운트 → 수요 선행지표 | 내국인 소비 트렌드 | SMIC 파마리서치 (여우야 카페) |
| TikTok 조회수 | 제품/브랜드 관련 영상 조회수 추적 | 바이럴 마케팅 효과 검증 | SMIC 파마리서치 (크리스 제너 360만 조회) |
| Google Trends | 키워드 검색 지수 월별 추적 | 소비자 관심도 proxy | 범용 |
| Amazon 리뷰 수 | 제품 리뷰 누적 추이 | 해외 시장 침투 속도 | SMIC 파마리서치 |
| AGF/행사 참석인원 | 연도별 참석인원 | 서브컬처 시장 성장 | SMIC 애니플러스 (AGF 72,081명) |

### 19-4. 공공데이터 활용

| 데이터 소스 | 종류 | 활용 예시 |
|------------|------|----------|
| 건강보험심사평가원 | 가입자/상실자, 진료 건수 | 의사 인력 변동, 시술 건수 추정 |
| 관세청 수출입통계 | 품목별 수출입액 | 수출 기업 매출 검증 |
| 한국은행 ECOS | 금리, 환율, GDP | 매크로 변수 |
| 산업통상자원부 | 생산/출하/재고 | 제조업 경기 판단 |
| 영화진흥위원회 Kobis | 일별 관객수/매출 | 콘텐츠 기업 IP 수익 추정 |
| 전력거래소 | 전력 소비량 | 데이터센터/제조업 가동률 proxy |

### 19-5. 1차 데이터 Appendix 포맷

```
Appx N. [데이터 유형] (수집일: YYYY.MM.DD)

수집 방법: [크롤링/인터뷰/공공데이터 다운로드]
수집 건수: [N건/N명/N개월]
수집 범위: [기간, 지역, 플랫폼]
원시 데이터: [테이블로 전수 제시]

출처: [플랫폼명], CUFA [팀명]
```


## 20. 고급 매출추정 기법 (14개 벤치마크 종합)

기본 P×Q를 넘어서는 고급 추정 기법. 종목 특성에 따라 선택 적용.

### 20-1. 회귀분석 기반 매출 모델

외부 드라이버와 매출 간 통계적 관계가 강할 때 (R² > 0.85) 적용.

**필수 산출물**:
1. 산점도 + 회귀선 SVG (`svg_scatter()` + 회귀선 overlay)
2. 회귀식: `Y = aX + b` (계수, 절편 명시)
3. R² 값 명시 (결정계수)
4. 추정 근거 서술: "일본 현지 신작 수(X)와 동사 콘텐츠 매출(Y) 간 R²=0.94의 강한 양의 상관"

벤치마크: SMIC 애니플러스 (일본 신작 애니 수 → 콘텐츠 매출, R²=0.94)

### 20-2. 자회사별 개별 추정

연결 자회사가 5개 이상이고 각각의 사업 특성이 다른 경우, 사업부 단위가 아닌 자회사 단위로 P×Q.

```
연결 매출 = Σ(자회사_i 매출) - 내부거래 제거
```

테이블 패턴:
```python
table(
    ["자회사", "P (ASP)", "Q", "매출", "YoY", "추정 근거"],
    [
        ["본사 콘텐츠", "—", "—", "150억", "+12%", "일본 신작수 회귀(R²=0.94)"],
        ["라프텔", "4,900원/월", "45만명", "265억", "+28%", "AVOD→SVOD 전환 14만명"],
        ["애니맥스", "—", "—", "80억", "+35%", "귀멸 IP 방영권"],
        ...
        ["합계", "", "", "850억", "+22%", "내부거래 제거 후"],
    ],
    highlight_rows={-1}
)
```

벤치마크: SMIC 애니플러스 (7개 자회사 개별 추정)

### 20-3. 선행지표 식별 및 활용

BS 항목(무형자산, CapEx, 재고자산)과 미래 매출 간 시차 상관분석.

**절차**:
1. BS 항목과 1~4분기 래깅된 매출 간 상관계수 산출
2. R² > 0.90인 관계 발견 시 선행지표로 공식 채택
3. dual-axis 차트로 시각화 (좌: 선행지표, 우: 매출, 시차 표시)
4. 해당 선행지표의 최근 값으로 향후 매출 preview

벤치마크: SMIC 애니플러스 (무형자산 투자액 → 1분기 후 콘텐츠 매출, R²=0.9825)

### 20-4. OSMU / 승수효과 정량화

IP/콘텐츠 기업에서 원작 매출 대비 파생 수익(굿즈, 게임, 라이선싱 등)의 배수.

| IP 사례 | 원작 매출 | 파생 매출 | OSMU 배수 |
|---------|----------|----------|----------|
| Star Wars | 영화 $10.3B | 굿즈/게임 $42B | 3,200% |
| Lion King | 영화 $1.7B | 뮤지컬/굿즈 $8.1B | 490% |
| Toy Story | 영화 $3.1B | 굿즈/테마파크 $16B | 530% |
| **평균** | | | **740%** |

적용 예: "귀멸의 칼날 무한성 극장 수익 22억원 × OSMU 배수 740% → 파생 수익 ~163억원 → 보수적 조정 186억원"

벤치마크: SMIC 애니플러스


### 20-5. 정량 분석 도구 체인 (v13.1, awesome-data-analysis 기반)

보고서 근거 강화를 위한 통계/분석 방법론. Phase 0 데이터 탐색 + Phase 4 본문 작성에 활용.

#### 활용 가능한 분석 방법론

| 방법론 | 용도 | Python 구현 | 보고서 적용 예시 |
|--------|------|------------|----------------|
| **피어슨 상관분석** | 변수 간 선형 관계 | `scipy.stats.pearsonr` | ASP vs 원유가, 수주 vs 매출 |
| **단순/다중 회귀** | 드라이버→매출 인과 | `sklearn.linear_model` | 신작수→콘텐츠매출 (R²=0.94, SMIC 패턴) |
| **시계열 분해** | 트렌드/계절성 분리 | `statsmodels.tsa` | 분기 매출 계절성, 사이클 위치 |
| **이상치 탐지** | 재무 데이터 품질 | `PyOD` / IQR | 비정상적 마진 변동 검출 |
| **분포 피팅** | ASP/마진 분포 파악 | `scipy.stats.fit` | 1차 가격조사 30건의 분포 분석 |
| **부트스트랩** | 추정값 신뢰구간 | `numpy.random` | 목표주가 95% CI 산출 |
| **몬테카를로 시뮬** | 확률 기반 DCF | `random/numpy` | WACC×g 10,000회 시뮬레이션 |
| **ROC/정밀도** | 선행지표 유효성 | `sklearn.metrics` | BS 선행지표→매출 예측력 검증 |

#### 자동 EDA 패턴 (Phase 0)

Phase 0에서 MCP로 수집한 재무 데이터를 자동 탐색하는 절차:
```
1. 결측치 비율 체크 → 빈칸 표시 (mock 금지)
2. 이상치 탐지 (IQR 방식) → 비정상 마진/매출 구간 식별
3. 재무 변수 간 상관관계 매트릭스 → 핵심 드라이버 후보 선별
4. 시계열 분해 → 매출의 트렌드/계절성/잔차 분리
5. 분석 결과를 config.py의 NARRATIVE에 자연어로 반영
```

#### Evaluator 체크 (v13.1)
- 보고서에 **최소 1개 통계 분석** 포함 필수 (R², p-value, 상관계수 중 1개+)
- 회귀분석 사용 시: 산점도+회귀선 SVG + R² 명시 + 회귀식 공개 필수

## 21. 독자적 분석 프레임 템플릿

매 보고서에 1개 이상의 종목/산업 고유 분석 도구를 개발하여 차별화.

### 21-1. 명명 규칙

`"[기업/산업명] [지표명]"` 형식. 측정 가능하고, 시간에 따라 추적 가능하며, 이 분석에서만 사용되는 고유 개념.

### 21-2. `proprietary_metric()` 헬퍼

```python
def proprietary_metric(name, formula, description, tracking, viz_html=""):
    """독자적 분석 프레임 블록

    Args:
        name: 지표명 (e.g., "키움 Multiplier")
        formula: 산식 (e.g., "K% / G% (키움 수수료 수익 성장률 / 시장 거래대금 성장률)")
        description: 지표 의미 설명 2~3문장
        tracking: 추적 방법 (e.g., "분기별 공시 기반 산출, 과거 5년 평균 109.2%")
        viz_html: 시각화 HTML (차트 등, 선택)
    """
    h = f'''<div style="background:var(--purple-bg);border:1px solid var(--purple-border);padding:20px;margin:20px 0;border-radius:4px;">
    <p style="color:var(--purple-light);font-size:16px;font-weight:700;margin-bottom:8px;">{name}</p>
    <p style="color:var(--text);font-size:13px;margin:4px 0;"><strong>산식:</strong> {formula}</p>
    <p style="color:var(--text);font-size:13px;line-height:1.7;margin:8px 0;">{description}</p>
    <p style="color:var(--text-sec);font-size:12px;"><strong>추적:</strong> {tracking}</p>
    {viz_html}
    </div>'''
    return h
```

### 21-3. 사례 아카이브

| 지표명 | 산식 | 기업/산업 | 출처 |
|--------|------|----------|------|
| 키움 Multiplier | K%/G% (키움 수수료 성장률 / 시장 거래대금 성장률) | 키움증권 | YIG 3조 |
| 시너지 실현률(SRR) | 실현 시너지 / 발표 시너지 × 100 (분기별 추적) | HD건설기계 | CUFA (자체) |
| OSMU 배수 | 파생수익 / 원작수익 × 100 | 콘텐츠 기업 | SMIC 애니플러스 |
| 리쥬란 침투율 | 리쥬란 시술건수 / 전체 피부시술건수 | 파마리서치 | SMIC 2팀 |
| HBM 쇼티지율 | (수요 스택수 - 공급 스택수) / 수요 스택수 × 100 | 반도체 장비 | S.T.A.R |


## 22. 용어 정리 (Glossary) 구현 상세

### 25-1. 배치 위치

TOC 직후, Key Chart 인트로와 동일 페이지 또는 바로 직후. `id="glossary"`로 TOC에서 링크.

### 25-2. `gen_glossary()` 헬퍼

```python
def gen_glossary(terms):
    """용어 정리 테이블 (YIG 키움증권 벤치마크)

    Args:
        terms: [(용어, 정의, 영문), ...] 10~15개

    Example:
        gen_glossary([
            ("OPM", "영업이익을 매출액으로 나눈 비율. 본업의 수익성 지표", "Operating Profit Margin"),
            ("WACC", "기업의 자금 조달 비용의 가중 평균. DCF 할인율로 사용", "Weighted Average Cost of Capital"),
            ("P×Q", "가격(Price)×수량(Quantity) 방식의 매출 추정법", "Price × Quantity"),
            ...
        ])
    """
    h = '<div id="glossary" style="margin:32px 0;">\n'
    h += '<h3 style="font-size:18px;color:var(--purple-light);margin-bottom:16px;">용어 정리</h3>\n'
    h += table(
        ["용어", "정의", "영문"],
        [[t, d, e] for t, d, e in terms],
        sec=0, title="산업 핵심 용어", src="CUFA 정리"
    )
    h += '</div>\n'
    return h
```

### 25-3. 최소 요구사항

- **최소 10개, 권장 15개**
- 섹션1~2에서 처음 등장하는 산업 특화 용어 전부 포함
- 밸류에이션 용어 (PER, PBR, EV/EBITDA, WACC, DCF, FCFF, beta 등)도 비전공자 배려하여 포함
- 금융업이면 종투사/발행어음/NCR 등 업종 특화 용어 필수 (YIG 키움증권 사례)


## 23. Key Chart 인트로 구현 상세

### 23-1. `gen_key_charts()` 헬퍼

```python
def gen_key_charts(charts_4):
    """Key Chart 인트로 페이지 (YIG 키움증권 벤치마크)
    TOC 직후 배치. 보고서 전체 메시지를 차트 4개로 즉각 전달.

    Args:
        charts_4: [(svg_html, caption), ...] 정확히 4개
        caption: 1줄 핵심 메시지 (e.g., "매출 CAGR +15%, OPM 구조적 개선")
    """
    h = '<div id="key-charts" style="margin:40px 0;">\n'
    h += '<h3 style="font-size:18px;color:var(--purple-light);margin-bottom:24px;text-align:center;">Key Charts</h3>\n'
    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">\n'
    for svg, caption in charts_4:
        h += f'<div style="text-align:center;">\n{svg}\n'
        h += f'<p style="font-size:12px;color:var(--text-sec);margin-top:8px;line-height:1.4;">{caption}</p>\n</div>\n'
    h += '</div></div>\n'
    return h
```

### 23-2. 차트 선택 가이드

보고서 유형에 따른 4개 차트 선택:

| 위치 | 기업분석 보고서 | 산업 보고서 |
|------|---------------|-----------|
| 좌상 | 매출/OPM 추이 (핵심 실적) | 시장 규모 추이 |
| 우상 | 목표주가 도달 경로 (현재가→목표가) | TAM/SAM/SOM |
| 좌하 | 핵심 IP 관련 차트 (시너지/파이프라인/점유율) | 경쟁 구도 |
| 우하 | Peer 비교 산점도 (OPM vs PER) | 밸류체인 |


## 24. 산업보고서 모드

S.T.A.R(성균관대)의 GaN 반도체/중국 반도체 굴기 보고서 분석 결과, 산업+기업 복합 보고서의 차별화된 구조 확인.

### 24-0a. 산업별 분기 규칙 (v9)

P×Q Bottom-up이 모든 산업에 적합하지 않다. 산업 특성에 따라 매출 추정 방법을 분기:

| 산업 유형 | 매출 추정 방법 | 핵심 KPI | 예시 |
|---------|-------------|---------|------|
| **제조업** | P×Q (제품별 ASP × 판매량) | 가동률, CAPA, ASP, 수주잔고 | 한국콜마, HD건설기계, 삼양식품 |
| **금융업** | 사업부별 수익 (이자/비이자/수수료) | NIM, 예대율, 수수료율, CIR | 미래에셋증권, 키움증권 |
| **플랫폼/IT** | KPI 기반 (MAU × ARPU) | MAU, DAU, 전환율, ARPU, Take rate | NAVER, 카카오 |
| **통신** | 가입자 × ARPU | 가입자수, 해지율, 5G 전환율 | SK텔레콤 |
| **유통/서비스** | 점포 × 점당 매출 | 점포수, 동일점 성장률, 객단가 | 이마트, CJ올리브영 |
| **바이오** | 파이프라인별 확률 가중 (rNPV) | 임상 단계, 성공 확률, TAM | 셀트리온, 알지노믹스 |
| **건설/조선** | 수주잔고 전환 (매출인식 타이밍) | 수주잔고, 공정률, 인도 스케줄 | SK오션플랜트 |
| **에너지/소재** | 스프레드 × 처리량 | 정제마진, 가동률, 원유 가격 | S-Oil |
| **적자 성장주** | TAM × 점유율 → PSR | 매출 성장률, BEP 시점, 번레이트 | 씨어스테크놀로지 |
| **지주사/다사업부** | SOTP (사업부별 EV 합산) | 사업부별 EV/EBITDA, 지분율, 할인율 | HD현대중공업, 두산 |

**Valuation 방법론도 산업별 분기:**
| 산업 | 주 Valuation | 보조 Valuation | 비고 |
|------|------------|---------------|------|
| 제조업 일반 | PER | DCF | Forward EPS 기준 |
| 금융업 | PBR | DDM or RIM | ROE-PBR 회귀 |
| 적자기업 | PSR | DCF(BEP 이후) | 매출 성장률 기반 |
| 지주사 | SOTP | NAV | 사업부별 분리 |
| 바이오 | rNPV | PER(흑자전환 후) | 임상 확률 가중 |
| 부동산/리츠 | NAV | 배당수익률 | FFO 기반 |
| 시클리컬 | PBR | EV/EBITDA | 이익 변동성 높아 PER 부적합 |

### 20-5b. v9 추가 Valuation 방법론 (P1, 7종)

**EV/Sales**: `EV/Sales = EV / 매출`. 적자 성장주 필수 (PSR과 다름 — EV/Sales은 자본구조 반영).
**EV/EBIT**: `EV/EBIT = EV / EBIT`. D&A >> CapEx인 기업(반도체, 조선)에서 EV/EBITDA보다 정확.
**PEG Ratio**: `PEG = PER / EPS성장률(%)`. <1.0 저평가, 1.0 적정, >1.5 고평가. 성장주 보조검증.
**Reverse DCF**: 현재 주가를 고정 → 내재성장률(g_implied) 역산. "시장은 몇 % 성장을 반영하고 있는가?" → 내 추정과 비교하여 Upside 근거 제시. **모든 보고서에 필수.**
**NAV**: `NAV = Sum(자산시가) - 부채`. 지주사/부동산/투자회사 필수. 한국 지주사 할인율 30~40%.
**FCFE**: `FCFE = NI + D&A - CapEx - ΔNWC + 순차입변동`, `Ke = Rf + β×MRP`. 금융업(은행/보험/증권) 전용.
**DDM**: `V = Sum(DPS_t/(1+Ke)^t) + DPS_{n+1}/(Ke-g)/(1+Ke)^n`. 안정배당 5년+ 기업, 유틸리티/REIT.

### 20-5c. Reverse DCF 프레임워크 (모든 보고서 필수)

```
Step 1: DCF로 목표주가 산출 (예: 85,000원)
Step 2: 현재가(60,000원)를 고정 → g_implied 역산 (예: 8%)
Step 3: 비교 → "시장은 8% 성장만 반영, 당사 추정 15% → 7%p 갭이 업사이드 근거"
Step 4: 보고서 Valuation 섹션에 한 문단으로 서술
```

### 20-5d. 배제 근거 라이브러리 ("Why not Y?" 자동 생성용)

| 배제 방법론 | 표준 배제 사유 |
|-----------|-------------|
| PER | 적자로 PER 산출 불가 |
| PBR | 자산경량, BPS 대비 사업가치 미반영 |
| EV/EBITDA | EBITDA 음수 |
| EV/Sales | 마진율 차이 큰 Peer로 왜곡 |
| DCF | 영업이력 3년 미만, CF 추정 불가 |
| FCFE | 비금융업, FCFF 대비 이점 없음 |
| DDM | 무배당으로 적용 불가 |
| RIM | 자본변동성 과대, BPS 추적 불안정 |
| rNPV | 비제약 기업, Phase별 확률 부적용 |
| SOTP | 단일사업, 분할 불필요 |
| NAV | 무형자산 중심, 자산기반 부적합 |
| PEG | EPS 성장률 음수, PEG 무의미 |

### 20-5e. Korea Discount 정량화 (한국 종목 전용)

```
방법1 — PBR 국제비교: 한국 PBR = 선진국의 58%
방법2 — 회귀분석: ln(PBR) = a + b1×ROE + b2×Growth + b3×Korea_Dummy
방법3 — 산업매칭: 동사 PER vs 글로벌 Peer PER 할인율
원인: 지배구조 30~40%, 주주환원 20~30%, 지정학 10~15%
```

밸류에이션 섹션에서 "한국 시장 할인이 반영되어 있으며, 밸류업 프로그램에 의한 디스카운트 해소 가능성"을 정량적으로 서술.

### 21-1. Part 기반 구조

기업분석 보고서의 11섹션과 달리 Part 구조 사용:

```
Part 1: 산업 개요 + 기술 기초 (소재 물성, 공정, 밸류체인)
Part 2: 수요 동인 (시장별/용도별 세분화)
Part 3: 공급 구조 + 경쟁 환경
Part 4: 밸류체인 + 투자 전략 (병목 지점 → 수혜 기업)
Part 5: 기업분석 (개별 종목 1~3개, 간략 투자포인트)
```

### 21-2. 기업분석 모드와 차이점

| 항목 | 기업분석 보고서 | 산업보고서 |
|------|---------------|-----------|
| 구조 | 11섹션 (번호) | 5 Part (테마) |
| Valuation | 필수 (목표주가 산출) | N/R 또는 간단 상대가치 |
| P×Q 매출추정 | 필수 (사업부별) | 없음 (TAM/SAM/SOM 대체) |
| Appendix | IS/BS/CF 필수 | 없음 또는 간략 |
| 도표 넘버링 | "도표 X-Y" | "도표 N" (순번) |
| 핵심 차트 유형 | 실적 추정, PER Band | 시장 규모, 점유율, 기술 비교 |
| 목표 분량 | 75,000자+ | 50,000자+ |
| 캐치프레이즈 | 종목 테마 | 산업 테마 ("GaN다 GaN다 뿅 GaN다!") |

### 21-3. 트리거 분기

```python
# 사용자 요청에 따라 분기
if "산업보고서" in request or "산업분석" in request or "thematic" in request:
    # Part 기반 구조, Valuation 없음, TAM/SAM/SOM 중심
    mode = "industry"
else:
    # 기본: 11섹션 기업분석 보고서
    mode = "equity"
```

### 21-4. 산업보고서 필수 요소 (S.T.A.R 벤치마크)

- 기술 깊이: 소재 물성/공정 수준까지 설명 (GaN: 밴드갭, HEMT, 에피택셜)
- 수요-공급 정량 분석: 수요량 → 부품 개수 → 공급량 → 갭 산출 (병목 체인)
- 주요 플레이어 비교표: TOP 10 기업 × 5~6개 지표
- 정책/규제 매핑: 국가별 규제 현황 테이블
- 투자 전략 명시: "어떤 밸류체인 포지션에 투자해야 하는가" 결론

---

## 25. v9 개선사항 (2026.03.28, YIG/SMIC/STAR/EIA 14건 종합 벤치마크)

### 25-1. Compliance Notice 자동 삽입 (필수)

모든 보고서(HTML) 마지막에 자동 삽입. EIA 인텔리안테크 보고서 기반 + 학회 특성 반영.

```html
<section id="compliance" class="compliance-notice">
  <h3>Compliance Notice</h3>
  <ul>
    <li>본 보고서는 CUFA 가치투자학회의 교육·연구 목적 자료이며, <strong>투자 권유 또는 투자자문에 해당하지 않습니다.</strong></li>
    <li>본 보고서에 포함된 분석, 의견, 목표주가는 작성 시점의 정보에 기반하며, 향후 변경될 수 있습니다.</li>
    <li>본 보고서의 작성자는 해당 종목에 대해 보유/미보유 여부를 아래에 명시합니다.</li>
    <li>투자 결정에 따른 모든 책임은 투자자 본인에게 있습니다.</li>
    <li>본 보고서의 데이터는 DART, ECOS, KRX, FRED 등 공개 출처에서 수집하였으며, AI 도구(Claude Code + Nexus MCP)를 활용하여 작성되었습니다.</li>
    <li>본 보고서의 무단 복제·배포를 금합니다.</li>
  </ul>
  <table class="holdings-table">
    <tr><th>작성자</th><th>보유 여부</th><th>비고</th></tr>
    <!-- 팀원별 채우기 -->
  </table>
  <p class="ai-watermark">AI-Assisted Research Report — Data collected via Nexus Finance MCP, reviewed by human analysts</p>
</section>
```

(v13: HTML 전용 — DOCX 제거됨)

### 25-2. 민감도분석 히트맵 SVG 자동 생성 (필수)

모든 보고서에 최소 1개 민감도분석 포함. **14건 벤치마크 중 0건이 민감도분석을 포함했으므로 이것만으로 전 학회 대비 차별화.**

```python
def svg_sensitivity_heatmap(title, x_label, y_label, x_values, y_values, data_matrix, unit="원"):
    """
    민감도분석 히트맵 SVG 생성.

    Args:
        title: "WACC-영구성장률 민감도분석"
        x_label: "영구성장률 (%)"
        y_label: "WACC (%)"
        x_values: [0.0, 0.5, 1.0, 1.5, 2.0]
        y_values: [8.0, 9.0, 10.0, 11.0, 12.0]
        data_matrix: [[TP값들]] (y행 × x열)
        unit: "원" or "%"

    Returns:
        SVG string

    색상:
        목표주가 > 현재가: positive (#4ecdc4 계열)
        목표주가 < 현재가: negative (#ff6b6b 계열)
        기준 케이스: purple (#7c6af7) 하이라이트
    """
    # 구현은 build_template.py의 기존 SVG 패턴 활용
    pass
```

적용 대상:
1. **WACC × 영구성장률 → 목표주가** (DCF용, 필수)
2. **매출성장률 × OPM → EPS** (실적 민감도, 선택)
3. **ASP × 판매량 → 매출** (P×Q 민감도, 산업 특성에 따라)

### 25-3. Football Field 차트 SVG (필수)

```python
def svg_football_field(methods, current_price):
    """
    Football Field (가로 막대 범위 차트) SVG 생성.

    Args:
        methods: [
            {"name": "PER (Fwd)", "low": 45000, "base": 52000, "high": 60000},
            {"name": "PBR (Hist)", "low": 38000, "base": 44000, "high": 51000},
            {"name": "DCF", "low": 42000, "base": 55000, "high": 68000},
            {"name": "EV/EBITDA", "low": 40000, "base": 48000, "high": 56000},
            {"name": "확률가중 TP", "low": None, "base": 51200, "high": None},
        ]
        current_price: 39500

    Returns:
        SVG string — 가로 막대(low~high 범위) + base 마커 + 현재가 세로선
    """
    pass
```

색상: 범위 바는 그라데이션 (#7c6af7 → #a78bfa), 현재가는 red dashed line, 확률가중 TP는 gold.

### 25-4. DCF + 멀티플 이중 Valuation 강제

Evaluator 규칙 추가:

```
[Valuation 18점 필수 조건] — v9 추가
- 최소 2개 방법론 필수 (DCF + PER/PBR/EV-EBITDA 중 택1)
  - 1개 방법론만 사용 시: 최대 12점 (자동 -6점)
- 각 방법론의 "Why X? Why not Y?" 필수
  - 선택 근거 3문장 + 배제 사유 1문장씩
- Football Field 차트 필수
- 민감도분석 히트맵 1개+ 필수
- Implied PER sanity check 필수 (DCF 사용 시)
  - 터미널연도 내재 PER 산출 → >40x이면 경고 + 근거 서술
- 시나리오 확률 가중 TP 필수
  - Bull(20~30%)/Base(40~60%)/Bear(20~30%) 확률 명시 + 가중평균
```

### 25-5. 시나리오 확률 가중 TP 자동 계산

```python
def calculate_probability_weighted_tp(scenarios):
    """
    시나리오별 확률 가중 목표주가 산출.

    Args:
        scenarios: [
            {"name": "Bull", "tp": 68000, "prob": 0.25, "trigger": "신규 수주 대형 계약 체결"},
            {"name": "Base", "tp": 52000, "prob": 0.50, "trigger": "현재 추정치 달성"},
            {"name": "Bear", "tp": 38000, "prob": 0.25, "trigger": "수주 지연 + 원가 상승"},
        ]

    Returns:
        weighted_tp: 52500
        table_html: 시나리오 비교 테이블 HTML
    """
    weighted = sum(s["tp"] * s["prob"] for s in scenarios)
    return weighted
```

Valuation 섹션에 시나리오 테이블 + 확률 가중 TP 자동 삽입.

### 25-6. Implied PER Sanity Check + 시계열 (v9 강화)

DCF로 목표주가 산출 시 터미널연도의 내재 PER을 자동 계산.
**v9 추가: Implied PER 시계열 (SMIC 로보티즈 패턴)**:
```
연도별 Implied PER 추이를 테이블로 제시 → 성장 감소를 PER로 보여줌
| 연도 | 2026E | 2027E | 2028E | 2029E | 2030E | 2034E |
| Implied PER | 85.2x | 52.1x | 35.3x | 30.1x | 25.4x | 9.4x |
→ "현재 PER 85x는 과도해 보이나, 성장 반영 시 30E 25.4x로 수렴"
→ 시간 경과에 따른 PER 정상화 경로를 시각적으로 증명
```

```
Implied PER = 목표 시가총액 ÷ 터미널연도 순이익

예시 (SMIC 로보티즈):
- 목표 시총: 3,870억원 (2030E)
- 순이익: 152억원 (2030E)
- Implied PER = 25.39x → "합리적 범위"
- 만약 >40x → "⚠ 높은 수준. 터미널 성장률 또는 WACC 재검토 필요"
```

Evaluator가 자동 체크:
- ≤15x: "보수적" (green)
- 15~30x: "합리적" (blue)
- 30~40x: "공격적, 근거 보강 필요" (amber)
- >40x: "⚠ Red flag, 반드시 정당화" (red)

### 25-7. 주가 구간별 복기 섹션 (SMIC 파마리서치 패턴)

기업분석 보고서 섹션 2 또는 별도 "주가분석" 섹션:

```
## 주가분석 — 최근 1년 일봉 + 3년 구간별 복기

### 1년 일봉 차트 (필수)
- 데이터: pykrx 또는 stocks_history MCP — 최근 1년(약 250 거래일) 매거래일 종가
- SVG 라인 차트: X축=날짜(월 단위 라벨), Y축=주가(원)
- Y축 스케일: 최저가~최고가 범위로 (0부터 시작 금지! 변동이 안 보임)
- 거래량 하단 바 차트 병렬
- 현재가, 52주 최고/최저, 목표주가 수평선 표시
- KOSPI/업종지수 대비 상대강도 오버레이 (선택)

### 3년 구간별 복기
구간 1 (2023.01~2023.06): +45% | 신규 수주 발표 + 실적 서프라이즈
구간 2 (2023.07~2024.01): -22% | 금리 인상 + 수주 지연 우려
구간 3 (2024.02~2024.08): +30% | 해외 법인 흑자전환 + 밸류업
구간 4 (2024.09~현재): 횡보 | 시장 관망 + 신규 카탈리스트 대기
```

차트: 주가 라인 + 구간 색상 배경 + 이벤트 어노테이션 SVG.

### 25-8. 연결+별도 재무제표 동시 추정 (Appendix 강화)

SMIC만 하는 차별화 요소를 CUFA도 자동화:

```
=== 연결 (CFS, 필수) ===
Appendix A-1: 연결 포괄손익계산서 (CFS IS) — 5~7개년 (3A + 2~4E), 주요 계정 20행+
Appendix A-2: 연결 재무상태표 (CFS BS) — 동일 기간
Appendix A-3: 연결 현금흐름표 (CFS CF) — 동일 기간
Appendix A-4: 연결 매출원가 및 판관비 추정 — 계정과목별 % of sales (SMIC 핵심)
Appendix A-5: 연결 금융손익 추정 — 이자수익/비용, FVPL, 파생상품, 외환, 유효이자율 역산
Appendix A-6: 연결 법인세비용 추정 — 유효법인세율 산출

=== 별도 (OFS, 권장) ===
Appendix A-7: 별도 포괄손익계산서 (OFS IS)
Appendix A-8: 별도 재무상태표+현금흐름표 (OFS BS & CF)
Appendix A-9: 별도 금융손익 추정
Appendix A-10: 별도 매출원가 및 판관비 추정
Appendix A-11: 별도 무형자산상각비 추정 (해당 시)

=== 공통 (필수) ===
Appendix A-12: 주당지표 (EPS/BPS/DPS/CFPS, PER/PBR/배당수익률)
Appendix A-13: P×Q 확장 (사업부별 ASP/Q 5개년)
Appendix A-14: DCF 민감도 + WACC 상세
Appendix A-15: Peer 비교 테이블 (글로벌 TOP 10)
Appendix A-16: 투자 체크리스트 (19개 항목)
```

**SMIC 대비 우위**: SMIC는 11개(연결5+별도6), CUFA는 **16개**(연결6+별도5+공통5).
핵심 차별화: A-4(매출원가 계정과목별 % of sales)와 A-5(금융손익 유효이자율)는 SMIC S등급의 핵심.
모든 Appendix 테이블은 2021~2028E (7~8개년) 최대 범위로 작성.
**전부 필수**: A-1~A-16 모두 필수. 권장/선택 없음. 별도 재무제표도 반드시 포함.

### 25-8b. 데이터 출처 엑셀 (필수 아웃풋)

모든 보고서는 HTML과 함께 **`{종목명}_재무데이터.xlsx`** 를 반드시 생성한다.

**v9 추가: 시나리오별 P&L 시트 분리 (SMIC 로보티즈 패턴)**:
```
Sheet 13: "PL_Bull" — Bull Case 손익계산서 (드라이버 가정 별도 명시)
Sheet 14: "PL_Bear" — Bear Case 손익계산서
Sheet 15: "시나리오_가정" — Bull/Base/Bear별 핵심 가정 비교표
  | 구분 | Bear | Base | Bull | 근거 |
  | 점유율 | 4% | 5% | 7% | 경쟁사 자제화율 기준 |
  | ASP | 15만 | 18만 | 22만 | 1차 가격조사 30건 기준 |
```

엑셀 구조:
```
Sheet 1: "IS_CFS" — 연결 손익계산서 (실적+추정, MCP 원본 데이터)
Sheet 2: "BS_CFS" — 연결 재무상태표
Sheet 3: "CF_CFS" — 연결 현금흐름표
Sheet 4: "IS_OFS" — 별도 손익계산서
Sheet 5: "BS_OFS" — 별도 재무상태표
Sheet 6: "CF_OFS" — 별도 현금흐름표
Sheet 7: "PxQ" — 사업부별 ASP/Q/매출 분해
Sheet 8: "Valuation" — DCF 가정, 멀티플, 민감도, WACC 상세
Sheet 9: "Peer" — Peer 기업 비교 데이터
Sheet 10: "Macro" — 금리/환율/GDP 등 매크로 변수
Sheet 11: "Stock_Price" — 주가 데이터 (최근 1년, 매거래일 종가/거래량, KRX pykrx 기준)
Sheet 12: "데이터출처" — ★ 핵심 시트: 모든 데이터의 출처 매핑
```

**"데이터출처" 시트 구조**:
| 데이터 항목 | 값 | 출처 | MCP 도구명 | 수집 일시(KST) | 검증 여부 |
|------------|---|------|-----------|--------------|----------|
| 매출액 2025A | 1,234,567백만원 | DART 사업보고서 | dart_financial_statements | 2026-03-28 14:30 | O |
| 기준금리 | 3.00% | 한국은행 | ecos_get_base_rate | 2026-03-28 14:31 | O |
| 주가 | 45,200원 | KRX | stocks_quote | 2026-03-28 14:32 | O |

**핵심 원칙**:
- 엑셀의 모든 데이터는 MCP 또는 공개 출처에서 수집한 **실제 데이터만** 포함
- **목업/임의 데이터 절대 금지** — MCP에서 못 가져온 셀은 비워두고 "수동 입력 필요" 표시
- 찬희님이 엑셀을 열면 **어떤 숫자가 어디서 왔는지 100% 추적 가능**해야 함
- 보고서 HTML의 모든 수치는 이 엑셀에서 가져온 것이어야 함 (원본 일치)

MCP 데이터 수집: `dart_financial_statements(corp_name, report_type="CFS")` + `dart_financial_statements(corp_name, report_type="OFS")`

### 25-9. AI 생성물 표기

HTML 보고서 좌측 하단에 반투명 워터마크:

```css
.ai-watermark {
    position: fixed;
    bottom: 8px;
    left: 12px;
    font-size: 10px;
    color: rgba(124, 106, 247, 0.4);
    z-index: 1000;
    pointer-events: none;
}
```

HTML 푸터에 "AI-Assisted Research | CUFA × Nexus MCP" 자동 삽입.

---

## 26. Nexus MCP 연동 확장 (v9)

### 23-1. 데이터 수집 최우선 순위

모든 데이터는 Nexus MCP를 최우선으로 사용. 139개 도구 중 보고서에 활용 가능한 전체 매핑:

| 보고서 섹션 | MCP 도구 | 용도 |
|------------|---------|------|
| **기업개요** | `dart_company_info`, `dart_search_company` | 기업 기본 정보 |
| **산업분석** | `macro_oecd`, `macro_imf`, `macro_worldbank` | 글로벌 TAM/SAM |
| | `academic_semantic_scholar`, `academic_arxiv` | 산업 관련 학술논문 |
| | `news_search`, `news_market_sentiment` | 산업 뉴스 + 감성 분석 |
| | `trade_korea_exports`, `trade_korea_imports` | 수출입 동향 |
| | `kosis_get_table`, `kosis_search_tables` | 국가통계 (생산지수, 산업 통계) |
| **기업분석** | `dart_financial_statements` | IS/BS/CF (CFS+OFS) |
| | `dart_financial_ratios` | 재무비율 |
| | `dart_major_shareholders` | 대주주 현황 |
| | `stocks_quote`, `stocks_history` | 주가 데이터 |
| | `stocks_beta` | 베타 계수 (WACC용) |
| **Peer 비교** | `us_stock_quote`, `us_company_profile` | 해외 Peer |
| | `val_peer_comparison` | 자동 Peer 비교 |
| | `val_cross_market_comparison` | 크로스마켓 비교 |
| **매크로** | `ecos_get_base_rate`, `ecos_get_exchange_rate` | 금리/환율 (WACC용) |
| | `ecos_get_gdp`, `ecos_get_cpi` | GDP/CPI |
| | `ecos_get_macro_snapshot` | 매크로 스냅샷 |
| | `macro_korea_snapshot` | 한국 매크로 |
| **밸류에이션** | `val_dcf_valuation` | DCF 자동 계산 |
| | `val_calculate_wacc` | WACC 자동 계산 |
| | `val_sensitivity_analysis` | 민감도분석 자동 |
| | `val_get_market_assumptions` | 시장 가정치 |
| **시각화** | `viz_line_chart`, `viz_bar_chart` | 차트 생성 |
| | `viz_heatmap` | 히트맵 (민감도) |
| | `viz_candlestick` | 캔들스틱 (주가) |
| | `viz_waterfall` | 워터폴 (비용 분해) |
| | `viz_scatter` | 산점도 (Peer OPM vs PER) |
| | `viz_dual_axis` | 이중축 (매출+OPM) |
| | `viz_sensitivity_heatmap` | 민감도 히트맵 |
| **부동산 기업** | `rone_get_market_summary`, `realestate_apt_trades` | 부동산 산업 데이터 |
| **에너지 기업** | `energy_crude_oil`, `energy_natural_gas` | 원유/가스 가격 |
| **해운 기업** | `maritime_bdi`, `maritime_container_index` | BDI/컨테이너 운임 |
| **크립토 기업** | `crypto_ticker`, `crypto_ohlcv` | 크립토 시세 |
| **뉴스/이슈** | `gdelt_search`, `gdelt_korea_news` | 글로벌/한국 뉴스 |
| | `news_keyword_volume`, `news_trend` | 키워드 트렌드 |
| **특허 분석** | `patent_search`, `patent_trending` | 기술 특허 동향 |
| **정책** | `politics_finance_bills`, `politics_recent_bills` | 금융 관련 법안 |

### 23-2. 글로벌 TAM/SAM/SOM 데이터 수집

산업분석에서 글로벌 시장 규모 추정 시:

```
1차: macro_worldbank, macro_oecd → GDP 대비 산업 비중
2차: academic_semantic_scholar → 시장 규모 추정 논문 검색
3차: news_search → 시장 보고서 인용 뉴스 검색
4차: gdelt_search → 글로벌 산업 동향 뉴스
```

**MCP에서 TAM 데이터를 직접 가져올 수 없는 경우**:
- 출처를 명시하고 "시장조사 기관 추정치" 기반으로 서술
- 절대 mock 데이터 사용 금지
- MCP `academic_*` 도구로 학술논문 기반 시장 규모 크로스체크

### 23-3. 다른 스킬과의 연동 파이프라인

cufa-equity-report 작성 시 다른 스킬을 보조적으로 활용:

```
cufa-equity-report (메인)
├── claude-deep-research-skill → 산업/기업 딥 리서치 (Phase 0)
│   └── 멀티소스 합성, 인용 추적, 신뢰도 점수
├── mla-dsa-analysis → 인터랙티브 분석 위젯 (Phase 2)
│   └── 클릭→상세 카드, 차원 비교, 아키텍처 다이어그램
├── research-report → 범용 보고서 빌드 도구 (Phase 2)
│   └── HTML 빌드 유틸, 차트 스타일, 보라 테마
├── competition-arsenal → 대회 프리셋 (Mode: competition)
│   └── 데이터 검증, 시각화, PPTX/XLSX 동시 생성
├── macro-dashboard → 매크로 차트 일괄 생성 (Phase 0)
│   └── 10대 거시지표 다크테마 PNG
└── Nexus MCP (139도구) → 데이터 수집 엔진 (Phase 0)
    └── DART, ECOS, KOSIS, pykrx, FRED, CCXT, Polymarket...
```

**연동 규칙**:
- cufa-equity-report가 **마스터 스킬** — 최종 산출물(HTML+Excel+MD) 책임
- 다른 스킬은 **서브 파이프라인**으로만 호출
- 데이터 수집은 반드시 Nexus MCP → 스킬 순서 (MCP 우선)

### 23-4. 외부 도구 통합 카탈로그 (v13.1, 2026.04 리서치 종합)

> 찬희가 제공한 GitHub 소스 전수 분석 후 보고서 파이프라인에 활용 가능한 도구 매핑.

#### 23-4a. Draw.io MCP — 다이어그램 자동 생성 (jgraph/drawio-mcp)

**용도**: MLA 밸류체인, DSA 시너지 아키텍처, 경쟁 구도 다이어그램을 AI가 자동 생성.
현재 인라인 SVG로 직접 구현하는 패턴의 **보조 도구**로 활용.

| 기능 | 설명 | 보고서 적용 |
|------|------|------------|
| `create_diagram` | draw.io XML → 인터랙티브 다이어그램 | 밸류체인, 프로세스 플로우 |
| `search_shapes` | 10,000+ 도형 검색 (AWS/Azure/UML/BPMN) | 산업별 아이콘 활용 |
| CSV→다이어그램 | 테이블 데이터 → 자동 다이어그램 | Peer 관계도, 지분 구조 |
| Mermaid 지원 | 코드 기반 다이어그램 | 빠른 프로토타이핑 |
| 출력: PNG/SVG/PDF | 내보내기 → HTML base64 삽입 | 보고서 이미지 |

**MCP 연결**: `https://mcp.draw.io/mcp` (설치 불필요, 호스팅형)
**적용 시점**: Phase 2 (HTML 빌드) — 복잡한 다이어그램이 필요할 때 draw.io MCP → SVG 추출 → HTML 삽입
**기존 인라인 SVG와 역할 분리**:
- 단순 차트 (바/라인/도넛): 기존 svg_* 헬퍼 (더 가벼움)
- 복잡한 아키텍처 다이어그램: draw.io MCP (10,000+ 도형 라이브러리)

#### 23-4b. KIS AI Extensions — 한국투자증권 실전 투자 연동 (koreainvestment/kis-ai-extensions)

**용도**: 보고서 작성 후 실제 투자 실행까지 연결하는 풀스택 파이프라인.
CUFA 보고서 → 투자 판단 → KIS로 모의/실전 매매.

| 컴포넌트 | 기능 | CUFA 연동 |
|---------|------|----------|
| **kis-strategy-builder** | 전략 설계 (10 프리셋 + 80 지표) | 보고서 IP → 매매 전략 변환 |
| **kis-backtester** | Lean 엔진 백테스트 + 파라미터 최적화 | 목표주가 검증용 역사적 시뮬 |
| **kis-order-executor** | BUY/SELL/HOLD 시그널 → 주문 실행 | 모의투자로 IP 검증 |
| **kis-team** | 전략→백테스트→주문 풀파이프라인 | 보고서 작성→투자 실행 자동화 |
| **MCP `run_backtest`** | 백테스트 실행 | IP의 매매 타이밍 검증 |
| **MCP `optimize_params`** | 파라미터 최적화 | 최적 진입/이탈 조건 탐색 |

**설치**: `npx @koreainvestment/kis-quant-plugin init --agent claude`
**인증**: `/auth vps` (모의) → `/auth prod` (실전)
**프리셋 전략 10종**: 골든크로스, 모멘텀, 52주신고가, 연속상승, 이격도, 돌파실패, 강한종가, 변동성확장, 평균회귀, 추세필터

**CUFA 보고서와의 연동 시나리오**:
```
Phase 0: MCP 데이터 수집 (Nexus MCP)
  ↓
Phase 1~4: 보고서 작성 (cufa-equity-report)
  ↓
Phase 6.5 (신규): 백테스트 검증 (KIS Backtest MCP)
  → 보고서 IP에서 진입/이탈 조건 자동 추출
  → KIS kis-backtest MCP로 전략 YAML 생성 + 1년 백테스트
  → 결과(승률/수익률/MDD/샤프) 추출 → 보고서 Appendix 삽입
  ↓
Phase 7 (신규): 투자 실행 검증
  → KIS kis-order-executor로 모의투자 진입
  → 분기별 실적 발표 후 보고서 복기 + 포지션 조정
```

**보안**: 실전 매매 시 반드시 사용자 확인 필수. 자동 매매 금지. 시그널 강도 0.5 미만 자동 스킵.

#### 23-4b-2. Phase 6.5 — 백테스트 검증 파이프라인 (v13.2)

**MCP 서버**: `kis-backtest` (http://127.0.0.1:3846/mcp, streamable-http)

Phase 6 HTML 빌드 완료 후, 보고서의 투자포인트(IP)를 자동으로 매매 전략으로 변환하여 백테스트 검증.

**Step 0: 전략 선택 인터랙션 (필수 — 찬희에게 물어볼 것)**

보고서 IP 분석 후 아래 테이블로 전략을 추천하고 **찬희에게 선택지를 제시**:

```
"Phase 6.5 백테스트를 진행합니다.
 보고서 IP를 분석한 결과, 아래 전략을 추천합니다:

 | # | 전략 | 추천 근거 | 프리셋 ID |
 |---|------|----------|-----------|
 | 1 | SMA 골든크로스 | IP1 CAPA 확장 모멘텀 | sma_crossover |
 | 2 | 52주 신고가 돌파 | IP2 신사업 기대감 | week52_high |
 | 3 | 이격도 반전 | IP3 밸류에이션 매력 | ma_divergence |

 → 번호로 선택하거나, 커스텀 전략을 직접 입력할 수 있습니다.
 → '전부' 입력 시 3개 전략 다전략 비교(batch) 실행
 → '최적화' 입력 시 선택한 전략의 파라미터 최적화 실행"
```

**IP 유형별 전략 추천 매핑**:

| IP 유형 | 추천 전략 (1순위) | 2순위 | 근거 |
|---------|-----------------|-------|------|
| CAPA 확장/매출 성장 | `sma_crossover` | `momentum` | 추세 추종이 성장주에 적합 |
| 신사업/모멘텀 | `week52_high` | `volatility_breakout` | 브레이크아웃 패턴 |
| 밸류에이션 매력 | `ma_divergence` | `short_term_reversal` | 이격도/과매도 반전 |
| 실적 서프라이즈 | `strong_close` | `consecutive_moves` | 실적 후 강한 종가 패턴 |
| 턴어라운드 | `short_term_reversal` | `false_breakout` | 반전 매매 |
| 배당/안정 | `trend_filter_signal` | `sma_crossover` | 장기 추세 필터 |

**커스텀 전략 추가 방법**:
```
찬희가 "PER 10 이하일 때 매수, PER 15 이상일 때 매도" 같은 조건을 말하면:
→ list_indicators로 사용 가능한 지표 확인
→ YAML 전략 코드 자동 생성
→ validate_yaml로 검증
→ run_backtest로 실행

예시 커스텀 YAML:
  name: "PER 밴드 전략"
  indicators:
    - alias: "SMA20"
      type: "SMA"
      params: { period: 20 }
  entry:
    conditions:
      - type: "cross_above"
        indicator: "SMA20"
  exit:
    conditions:
      - type: "cross_below"
        indicator: "SMA20"
```

**Step 1: IP → 전략 YAML 변환**
```
보고서 IP 3개에서 진입/이탈 조건 추출:
  IP 1: "CAPA 확장 → 매출 성장" → 매출 QoQ 10%↑ 시 진입
  IP 2: "신사업 모멘텀" → 뉴스 이벤트 기반 (수동 트리거)
  IP 3: "밸류에이션 매력" → PER Band 하단 진입, 상단 이탈

MCP 도구 사용:
  1. list_presets → 10개 프리셋 중 적합한 전략 선택
  2. get_preset_yaml(strategy_id, param_overrides) → YAML 생성
  3. validate_yaml(yaml_content) → 검증
```

**Step 2: 백테스트 실행**
```
MCP 도구 사용:
  1. run_backtest(yaml_content, symbols=["종목코드"], initial_capital=10000000)
     → job_id 반환 (비동기)
  2. get_backtest_result(job_id, wait=True, timeout=300)
     → 완료 시 결과 반환

결과 핵심 지표:
  - 총 수익률 (total_return)
  - 최대 낙폭 (max_drawdown, MDD)
  - 샤프 비율 (sharpe_ratio)
  - 승률 (win_rate)
  - 최대 연속 손실 (max_consecutive_losses)
```

**Step 3: 다전략 비교 (선택)**
```
MCP 도구 사용:
  run_batch_backtest(items=[
    {"strategy_id": "sma_crossover", "symbols": ["005930"], "param_overrides": {"fast_period": 10}},
    {"strategy_id": "momentum", "symbols": ["005930"]},
    {"strategy_id": "trend_filter_signal", "symbols": ["005930"]}
  ])
  → comparison: { by_sharpe, by_return, by_drawdown } 랭킹 반환
```

**Step 4: 보고서 삽입**
```
백테스트 결과를 HTML 테이블로 생성 → Appendix 또는 리스크 섹션에 삽입:

┌──────────────┬──────────┬──────────┬──────────┬──────────┐
│ 전략         │ 수익률   │ MDD      │ 샤프비율 │ 승률     │
├──────────────┼──────────┼──────────┼──────────┼──────────┤
│ SMA 크로스   │ +18.3%   │ -12.4%   │ 1.42     │ 58.3%    │
│ 모멘텀       │ +24.1%   │ -18.7%   │ 1.15     │ 52.1%    │
│ 추세필터     │ +15.7%   │ -8.9%    │ 1.68     │ 61.2%    │
└──────────────┴──────────┴──────────┴──────────┴──────────┘

주의: 백테스트 결과는 과거 데이터 기반이며 미래 수익을 보장하지 않음.
이 면책조항을 테이블 하단에 반드시 포함.
```

**파라미터 최적화 (고급)**
```
MCP 도구 사용:
  optimize_strategy(
    strategy_id="sma_crossover",
    symbols=["종목코드"],
    parameters=[
      {"name": "fast_period", "min": 5, "max": 20, "step": 5},
      {"name": "slow_period", "min": 20, "max": 60, "step": 10}
    ],
    target="sharpe_ratio"
  )
  → best_params + best_metrics 반환
```

#### 23-4c. QuantAgent — 기술적 분석 멀티에이전트 (Y-Research-SBU/QuantAgent)

**용도**: 보고서 주가분석 섹션에 기술적 분석 자동화. 현재 CUFA는 기본적 분석(펀더멘탈) 중심 → QuantAgent 패턴으로 기술적 분석 보강.

| 에이전트 | 기능 | CUFA 적용 |
|---------|------|----------|
| **Indicator Agent** | RSI, MACD, Stochastic 계산 | 주가분석 섹션 보조 지표 |
| **Pattern Agent** | 차트 패턴 인식 (삼중바닥/헤드앤숄더 등) | 주가 구간별 패턴 라벨링 |
| **Trend Agent** | 추세 채널 피팅 + 기울기 분석 | PER/PBR 밴드 보조 |
| **Decision Agent** | 종합 판단 (LONG/SHORT + 진입/이탈) | Catalyst Timeline 보조 |

**CUFA 보고서 적용 패턴**:
```
주가분석 (섹션 0-1) 강화:
1. 1년 일봉 차트 + 이벤트 어노테이션 (기존)
2. RSI/MACD 보조 지표 SVG 추가 (QuantAgent 패턴)
3. 추세 채널 + 지지/저항선 자동 피팅
4. "현재 기술적 위치: RSI 45 (중립), MACD 골든크로스 대기" 1줄 요약
```

**구현 방법**: QuantAgent 전체를 설치하지 않고, **지표 계산 로직만 차용**.
```python
# Phase 0에서 pykrx 주가 데이터로 기술적 지표 계산
import numpy as np

def calc_rsi(prices, period=14):
    """RSI 계산 (QuantAgent Indicator Agent 패턴)"""
    deltas = np.diff(prices)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])
    rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
    return 100 - (100 / (1 + rs))

def calc_macd(prices, fast=12, slow=26, signal=9):
    """MACD 계산"""
    ema_fast = pd.Series(prices).ewm(span=fast).mean()
    ema_slow = pd.Series(prices).ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line, macd_line - signal_line
```

**Evaluator 체크 (선택)**: 주가분석 섹션에 기술적 지표 1개+ 포함 시 가산점.

#### 23-4c-2. Jeff Sun 기술적 분석 지표 5종 (v13.2)

Jeff Sun(15년 경력 트레이더, $10M+ 운용)의 핵심 지표를 CUFA 주가분석에 보조 활용:

| 지표 | 산식 | 용도 | CUFA 적용 |
|------|------|------|----------|
| **ADR%** | 20일 평균 (고가-저가)/종가×100 | 변동성 측정 + 포지션 사이징 | 리스크 섹션 포지션 권장 |
| **RVoL** | 당일 거래량 / 50일 평균 거래량 | 수급 이상 탐지 | 주가분석 이벤트 라벨 |
| **ATR% from 50-MA** | (종가 - 50일MA) / ATR×100 | 과매수/과매도 + 이격도 | 진입 타이밍 판단 |
| **VARS** | RS × (1/변동성) 정규화 | 변동성 조정 상대강도 | Peer 비교 보조 |
| **VCP** | 고저차 수렴 패턴 탐지 | 브레이크아웃 사전 신호 | Catalyst Timeline 보조 |

```python
def calc_adr_pct(highs, lows, closes, period=20):
    """ADR% — 포지션 사이징의 기본 입력"""
    daily_range_pct = [(h-l)/c*100 for h,l,c in zip(highs, lows, closes)]
    return np.mean(daily_range_pct[-period:])

def calc_rvol(volumes, period=50):
    """RVoL — 당일 거래량 / 50일 평균"""
    return volumes[-1] / np.mean(volumes[-period:])

def calc_atr_pct_from_ma(closes, period_ma=50, period_atr=14):
    """ATR% Multiple from 50-MA — 이격도"""
    ma = np.mean(closes[-period_ma:])
    atr = np.mean([max(closes[i]-closes[i-1], abs(closes[i]-closes[i-1])) for i in range(-period_atr, 0)])
    return (closes[-1] - ma) / atr if atr > 0 else 0
```

**Jeff Sun Hard Rules (CUFA 투자 실행 시 적용)**:
1. 200일선 하회 시 매수 금지 — 하락추세 진입 방지
2. ATR% 4배 이상 이격 시 진입 금지 — 과매수 구간 추격 방지
3. 세션당 최대 3 신규 포지션 — 과도한 분산 방지
4. 실적 발표 직전/직후 진입 금지 — 이벤트 리스크 회피
5. 갭업 오프닝 시 극도 주의 — 30분 대기 후 진입 판단
6. 기존 수익 포지션 추가 > 신규 진입 — 승자 집중
7. 놓친 거래는 절대 추격하지 않는다 — FOMO 방지

#### 23-4d. Block Goose — 에이전트 오케스트레이션 레퍼런스 (block/goose)

**용도**: 서브에이전트 5개 병렬 빌드 패턴의 아키텍처 레퍼런스.
Goose = "로컬 확장형 오픈소스 AI 에이전트" (34.5K stars).

**CUFA 서브에이전트 패턴에 적용할 Goose 원칙**:
1. **자율 실행**: 서브에이전트가 섹션 작성 중 막히면 스스로 해결 시도 → 실패 시에만 메인에 보고
2. **MCP 확장성**: 서브에이전트마다 필요한 MCP 도구를 선택적으로 연결
3. **프로젝트 스케일**: 단일 파일이 아니라 프로젝트 전체를 이해하고 작업

**서브에이전트 구조 개선 (Goose + clawhip 영감)**:
```
메인 에이전트 (오케스트레이터)
├── cover.py 에이전트   ← config.py 읽고 표지/TOC/Key Charts 작성
├── industry.py 에이전트 ← DART 사업보고서 + 산업 데이터 기반
├── thesis.py 에이전트   ← IP 3개 + counter_arg + 인라인 반박
├── financial.py 에이전트 ← 재무분석 + Peer + 추정 + 밸류에이션
└── appendix.py 에이전트  ← 리스크 + Appendix 16개 + Compliance
    └── 각 에이전트에 전달: config.py 경로, 헬퍼 함수 목록, 최소 자수, DESIGN.md 규칙
```

#### 23-4e. 업비트 + 한국투자증권 실전 투자 파이프라인 (v13.1 비전)

> 찬희 요청: "실제 업비트와 한국투자증권 API를 활용해서 투자를 진행할 수 있어야 해"

**보고서 → 투자 실행 풀스택 비전**:
```
[Phase 0-6] CUFA 보고서 작성 (기존)
  → 투자의견: BUY, 목표주가: XX,XXX원
  ↓
[Phase 7] 투자 실행 (신규 비전)
  ├── 주식: KIS AI Extensions → 한국투자증권 API
  │   → kis-backtester로 전략 백테스트
  │   → kis-order-executor로 모의/실전 매매
  │   → /auth vps (모의) → /auth prod (실전)
  │
  ├── 크립토: 업비트 API (Nexus MCP crypto_* 도구 활용)
  │   → crypto_ticker: 실시간 시세
  │   → crypto_orderbook: 호가창
  │   → 직접 API: pyupbit 라이브러리
  │
  └── 복기: 분기별 실적 발표 후
      → 보고서 가정 vs 실적 비교
      → 엑셀 업데이트
      → 투자의견 재검토 (TP Revision History)
```

**보안 규칙**:
- 실전 매매는 반드시 찬희 수동 확인 후 실행
- API 키는 환경변수에서만 로드 (하드코딩 절대 금지)
- 모의투자로 최소 1개월 검증 후 실전 전환
- 단일 종목 포지션 한도: 총 자산의 20% 이하

**6레이어 안전장치 아키텍처 (v13.2, Jeff Sun + 찬희 설계)**:

에이전트가 실수로 전량 매도/매수하는 사고를 원천 차단하는 다중 방어선:

```
Layer 1 — 시그널 검증 (자동)
  시그널 강도 < 0.5 → 자동 스킵
  RSI/MACD/VARS 3개 지표 중 2개 이상 동의해야 실행
  
Layer 2 — 포지션 한도 (자동)
  단일 종목: 총 자산의 20% 이하
  단일 섹터: 총 자산의 40% 이하
  동시 보유: 최대 7종목
  세션당 신규 진입: 최대 3건 (Jeff Sun 규칙)

Layer 3 — 일일 손실 한도 (자동)
  일 최대 손실: 총 자산의 -2% → 자동 거래 중단
  주간 최대 손실: -5% → 1주 쿨다운
  "절대 2주 수익을 하루에 잃지 마라" (Jeff Sun 핵심 원칙)

Layer 4 — 인간 확인 (수동)
  실전 매매: 반드시 찬희 수동 승인
  모의투자: 자동 실행 허용 (로그 기록)
  포지션 변경 > 10%: 찬희 확인 필수

Layer 5 — 이벤트 회피 (자동)
  실적 발표 ±2일: 해당 종목 거래 금지
  FOMC/한은 금통위 ±1일: 전체 신규 진입 금지
  옵션 만기일(매월 셋째 금요일): 주의 모드
  분기말 리밸런싱(3/6/9/12월 말 3일): 주의 모드
  
Layer 6 — 긴급 정지 (Kill Switch)
  찬희 음성/텍스트 명령: "전 포지션 동결"
  시스템 이상 탐지: 5분 내 3건 이상 주문 → 자동 동결
  네트워크 장애: API 연결 실패 시 신규 주문 금지
```

**Phase 7: 투자 실행 복기 (v13.2, Jeff Sun 저널 시스템 기반)**

보고서 발행 후 분기별 복기 프레임워크:

```
Phase 7-A: 실적 발표 후 (분기별)
  → 보고서 추정치 vs 실적 비교 (IS 5개 항목)
  → IP별 적중/실패 판정
  → 엑셀 업데이트 + TP Revision History 추가
  
Phase 7-B: 트레이딩 저널 (Jeff Sun 7대 추적 지표)
  1. 승률 + R-Multiple: 수익 거래 비율 + 평균 수익/손실 배수
  2. 거래 보유 기간: 손실 거래 평균 보유일 vs 수익 거래 평균 보유일
  3. 진입 품질 점수: Hard Rules 준수율 (14개 중 몇 개 위반?)
  4. 포지션 관리 리뷰: 스케일링 결정 + 이익실현 타이밍 평가
  5. P&L 히스토그램: 일별/주별 손익 분포 시각화
  6. 숨겨진 개선 추적: YTD 수익률이 평탄해도 리스크 관리가 개선됐는지
  7. 정량화된 엣지 문서화: "어떤 패턴에서 엣지가 있었는지" 기록
  
Phase 7-C: 투자의견 재검토
  → Kill Condition 도달 여부 확인
  → 목표주가 유지/상향/하향/투자의견 변경 판단
  → TP Revision History에 변경 사유 기록
```

**스크리닝 + 워치리스트 체계 (v13.2, Jeff Sun 3단계)**

Phase 0에서 종목 선정 근거를 구조화하는 프레임워크:

```
Tier 1 — Stalk List (초기 스크리닝)
  14개 스크리너 결과 종합 (주간 업데이트)
  - 모멘텀: RS 상위 10%, 52주 신고가 근접
  - 펀더멘탈: OPM 개선, EPS 서프라이즈
  - 밸류: PER Band 하단, PBR 역사적 저점
  - 이벤트: 수주, 신제품, 규제 변화
  
Tier 2 — Focus List (정밀 검토)
  Stalk List에서 상위 10~15개 선별
  필수 충족: ① 상대강도 확인 ② 가격 셋업(VCP) ③ RVoL 확인 ④ 산업군 RS
  "A등급 아이디어만 실행 고려"
  
Tier 3 — 보고서 대상 (최종)
  Focus List에서 1~2개 선정
  CUFA 보고서 작성 → 팀 토론 → 투자의견 결정
  "왜 이 종목인가?"를 스크리닝 기준으로 정당화
```

#### 23-4f. TradingView MCP — 실시간 차트 데이터 접근 (tradesdontlie/tradingview-mcp)

**용도**: TradingView Desktop과 직접 연결하여 실시간 차트 데이터, 지표 값, Pine Script 자동화.
보고서 주가분석 + 기술적 분석 강화에 활용.

| 기능 | 설명 | 보고서 적용 |
|------|------|------------|
| `tv_health_check` | TradingView 연결 확인 | 데이터 수집 전 검증 |
| 차트 읽기 | 심볼/시간프레임/OHLC/거래량 500바 | 주가분석 실시간 데이터 |
| 지표 값 읽기 | RSI/MACD/볼린저 등 모든 지표 | 기술적 분석 보조 |
| Pine Script 그리기 | 선/라벨/테이블/상자 읽기 | 커스텀 지표 데이터 추출 |
| 전략 테스터 | 백테스트 결과/거래 목록 | 매매 전략 검증 |
| 스크린샷 | 차트 영역 캡처 | 보고서 이미지로 삽입 |
| Pine Script 자동화 | 작성→주입→컴파일→오류수정→재컴파일 루프 | 커스텀 지표 개발 |

**연결 방식**: Chrome DevTools Protocol (localhost, 데이터 외부 유출 없음)
**설치**: `git clone tradingview-mcp && npm install` → `~/.claude/.mcp.json`에 추가
**활용 시점**: Phase 0 (주가 데이터 수집) + Phase 1 (기술적 분석 리서치)

**CUFA 보고서 주가분석 강화 패턴**:
```
1. TradingView에서 종목 차트 로드
2. tv_get_chart_data → 500바 OHLC 추출
3. tv_get_indicator_values → RSI/MACD/볼린저 값 추출
4. tv_get_drawings → Pine Script 그리기 데이터 (지지/저항선)
5. tv_screenshot → 차트 스크린샷 → base64 → HTML 삽입
6. 추출 데이터를 config.py에 저장 → 주가분석 섹션에서 활용
```

#### 23-4g. claw-code/clawhip — 에이전트 알림 라우터 레퍼런스

**용도**: 서브에이전트가 빌드 중 진행 상황을 디스코드/슬랙으로 자동 알림하는 패턴.
clawhip = Git 커밋, GitHub PR, tmux 세션, 에이전트 수명주기 이벤트 → 채널 라우팅.

**CUFA 적용 가능 패턴**:
- 보고서 빌드 시작/완료를 디스코드 NEXUS 채널에 자동 알림
- HARD_MIN 검증 실패 시 찬희에게 즉시 알림
- Phase별 진행률 자동 보고 (Phase 0 완료 → Phase 1 시작 등)
- 구현: 기존 Luxon NEXUS 디스코드 봇 + webhook 활용

---

## 27. 디자인 일관성 규칙 (v9, 종목 불문)

어떤 종목이든 동일한 디자인 톤과 레이아웃으로 출력.

### 24-1. CSS 디자인 토큰 (절대 변경 금지 — 모든 보고서 동일)

기존 보고서 감사에서 **2개의 디자인 시스템이 공존**하는 문제 발견.
v9부터 아래 CSS 변수를 **단일 표준**으로 확정. 어떤 종목이든 이 값만 사용.

```css
:root {
  /* === 배경 === */
  --bg: #0a0a0a;
  --surface: #0f0f0f;
  --surface2: #141414;
  --border: #222222;
  --border2: #333333;

  /* === 퍼플 시그니처 === */
  --purple: #7c6af7;
  --purple-light: #a78bfa;
  --purple-bg: #12101f;
  --purple-border: #2d2654;

  /* === 텍스트 === */
  --text: #e0e0e0;
  --text-sec: #888888;
  --text-tert: #555555;

  /* === 시맨틱 === */
  --positive: #4ecdc4;
  --negative: #ff6b6b;
  --blue: #6cb4ee;
  --amber: #ffd93d;

  /* === 폰트 === */
  --font: 'Noto Sans KR', '맑은 고딕', 'Malgun Gothic', sans-serif;
  --font-size-body: 14px;
  --line-height: 1.8;

  /* === 레이아웃 === */
  --max-width: 1100px;
  --sidebar-width: 180px;       /* 고정값, 반응형에서 자동 해제 */
  --section-padding: 40px 0;
  --border-radius: 4px;         /* 4px 통일, 절대 8px 금지 */
  --content-padding: 0 24px;
}

/* === 폰트 로드 (필수) === */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');

/* === 통일 규칙 === */
body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: var(--font-size-body); line-height: var(--line-height); }
h1 { font-size: 36px; font-weight: 800; }
h2 { font-size: 22px; font-weight: 700; }
h3 { font-size: 17px; font-weight: 600; }
table thead th { background: var(--purple); color: #fff; font-size: 12px; }
.chart-box { background: var(--surface); border: 1px solid var(--border); border-radius: var(--border-radius); padding: 16px; }

/* === Counter-arg 통일 === */
.counter-arg { border-left: 3px solid var(--negative); background: rgba(255,107,107,0.04); padding: 16px 20px; margin: 16px 0; border-radius: var(--border-radius); }
.counter-arg .concern-label { color: var(--negative); font-weight: 700; font-size: 13px; }
.counter-arg .rebuttal-label { color: var(--positive); font-weight: 700; font-size: 13px; }

/* === Sidebar 통일 === */
.sidebar-layout { display: grid; grid-template-columns: var(--sidebar-width) 1fr; gap: 20px; }

/* === Sticky Header 통일 === */
.sticky-header { position: sticky; top: 0; z-index: 100; background: rgba(10,10,10,0.92); backdrop-filter: blur(8px); padding: 8px 24px; font-size: 13px; }

/* === Float TOC 통일 === */
.float-toc { position: fixed; right: 20px; top: 100px; width: 180px; background: rgba(15,15,15,0.9); border-radius: var(--border-radius); z-index: 90; }

/* === Footer 통일 === */
.report-footer { border-top: 2px solid var(--purple); padding: 40px 0; margin-top: 60px; }
.report-footer .author { font-size: 14px; font-weight: 700; color: var(--purple); }

/* === 모바일 반응형 (3단계 필수) === */
@media (max-width: 1200px) { .float-toc, .section-dots { display: none; } }
@media (max-width: 768px) {
  .sidebar-layout { grid-template-columns: 1fr; }
  .chart-pair { grid-template-columns: 1fr; }
  .cover-metrics { grid-template-columns: 1fr 1fr; }
  h1 { font-size: 28px; }
  h2 { font-size: 18px; }
}
@media (max-width: 480px) {
  .cover-metrics { grid-template-columns: 1fr; }
  table { font-size: 11px; }
  .sticky-header { font-size: 11px; padding: 6px 12px; }
  body { font-size: 13px; }
}

/* === 인쇄 === */
@media print {
  body { background: #fff; color: #000; font-size: 10pt; }
  .sticky-header, .float-toc, .section-dots, .progress-bar { display: none; }
  .counter-arg { border-left: 2px solid #333; }
  @page { size: A4; margin: 2cm; }
}
```

**금지 사항 (v9 확정)**:
- `border-radius: 8px` 사용 금지 → 항상 `4px`
- `#0D0D1A` (남색 배경) 사용 금지 → `#0a0a0a`만
- `#F5F3FF` (밝은 라벤더) 사용 금지 → `#12101f`만
- 테이블 헤더에 회색 배경 금지 → 항상 `var(--purple)` 보라
- 클래스명 변형 금지: `.sticky-bar`/`.sticky-hdr` → 항상 `.sticky-header`
- Google Fonts 미로드 금지 → `@import` 필수
- `z-index: 9998` 금지 → 최대 `100` (sticky), `90` (toc), `80` (기타)

### 24-1a. CUFA 보고서 디자인 시스템 — DESIGN.md 패턴 (v13.1, awesome-design-md 기반)

> VoltAgent/awesome-design-md의 DESIGN.md 구조를 CUFA 보고서에 적용.
> 목적: 서브에이전트가 이 섹션만 읽으면 디자인 시스템 전체를 파악하고 일관된 UI 생성 가능.

#### Visual Theme & Atmosphere
- **톤**: 신뢰, 정밀, 절제 (금융 리서치 전문성)
- **무드**: 다크+퍼플 — Goldman Sachs의 절제 + Stripe의 기술감
- **레퍼런스**: 증권사 리서치 보고서 + SMIC 2단 레이아웃
- **금지 무드**: 귀여움, 캐주얼, 네온, 게이밍, 스톡이미지 느낌

#### Color Palette & Roles
| 역할(Role) | 변수명 | 값 | 용도 |
|-----------|--------|-----|------|
| **Primary** | `--purple` | #7c6af7 | 브랜드, 헤더, 테이블 TH, CTA |
| **Primary Light** | `--purple-light` | #a78bfa | 호버, 보조 강조 |
| **Secondary** | `--blue` | #6cb4ee | Peer 비교, 보조 데이터 |
| **Positive** | `--positive` | #4ecdc4 | 상승, Beat, 긍정 |
| **Negative** | `--negative` | #ff6b6b | 하락, Miss, 리스크 |
| **Amber** | `--amber` | #ffd93d | 경고, 중립 변동 |
| **Background** | `--bg` | #0a0a0a | 최하위 배경 |
| **Surface 1** | `--surface` | #0f0f0f | 카드, 사이드바 |
| **Surface 2** | `--surface2` | #141414 | 차트박스, 테이블 행 |
| **Text** | `--text` | #e0e0e0 | 본문 |
| **Text Sec** | `--text-sec` | #888888 | 보조 텍스트, 출처 |
| **Border** | `--border` | #222222 | 구분선 |

**규칙**: 색상은 **항상 역할(role)에 바인딩**. 임의로 `#ff0000` 같은 하드코딩 금지 → 반드시 `var(--negative)` 사용.

#### Typography Scale
| 요소 | 크기 | 굵기 | 행간 |
|------|------|------|------|
| h1 (보고서 제목) | 36px | 800 | 1.3 |
| h2 (섹션 제목) | 22px | 700 | 1.3 |
| h3 (소제목) | 17px | 600 | 1.3 |
| body | 14px | 400 | 1.8 |
| small (출처, 캡션) | 12px | 400 | 1.4 |
| 숫자 | tabular-nums | — | — |

#### Component Catalog
| 컴포넌트 | 클래스 | border-radius | 특징 |
|----------|--------|:------------:|------|
| chart-box | `.chart-box` | 4px | surface bg, 1px border |
| counter-arg | `.counter-arg` | 4px | 3px left border (negative) |
| callout | `.callout` | 4px | 3px left border (purple) |
| insight-box | `.insight-box` | 4px | 1px border (positive) |
| expand-card | `.expand-card` | 4px | 클릭→펼침 |
| sidebar-layout | `.sidebar-layout` | 0 | 180px + 1fr grid |
| sticky-header | `.sticky-header` | 0 | z-index 100, blur(8px) |
| float-toc | `.float-toc` | 4px | z-index 90, right fixed |
| table | `table` | 0 | purple TH, tabular-nums TD |

#### Layout Grid
```
┌─ sticky-header (100% width, z:100) ─────────────────┐
│ 종목명 | 투자의견 | 목표주가 | 현재가                  │
└──────────────────────────────────────────────────────┘
┌─ report (max-width: 960px, centered) ───────────────┐
│ ┌─ sidebar (180px) ─┐ ┌─ content (1fr) ──────────┐  │
│ │ 해석적 키워드      │ │ Bold 첫문장 + 본문       │  │
│ │ 수치 + 메시지      │ │ 200~400자 문단 × 5      │  │
│ └──────────────────┘ └────────────────────────────┘  │
│ ┌─ chart-pair (1fr 1fr) ─────────────────────────┐  │
│ │ [chart-box A]          [chart-box B]           │  │
│ └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
┌─ float-toc (right, fixed, z:90) ─┐
│ ● 기업개요                         │
│ ● 산업분석 (active)                │
│ ● 투자포인트①                      │
└──────────────────────────────────┘
```

#### Do's and Don'ts
| DO | DON'T |
|-----|-------|
| CSS 변수(`var(--purple)`) 사용 | 하드코딩 `#7c6af7` |
| border-radius: 4px | border-radius: 8px |
| 데이터 밀도 우선 | 장식적 여백 남용 |
| role 기반 색상 | 임의 색상 |
| Noto Sans KR @import | 폰트 미로드 |
| backdrop-filter: blur | box-shadow |
| z-index: 100/90/80 | z-index: 9998 |
| 매 페이지 시각자료 | 텍스트만 페이지 |

#### Responsive Breakpoints
| 너비 | 변경 |
|------|------|
| >1200px | 풀 레이아웃 (sidebar + float-toc + dots) |
| 768~1200px | float-toc/dots 숨김, sidebar 유지 |
| 480~768px | sidebar→1col, chart-pair→1col |
| <480px | font-size 축소, sticky 축소, 테이블 11px |

#### Agent Prompt Guide (서브에이전트에게 전달)
```
이 보고서는 CUFA DESIGN.md 시스템을 따른다:
- 색상: var(--purple), var(--positive), var(--negative) 등 role 변수만
- 컴포넌트: chart-box, counter-arg, callout, sidebar-layout 클래스만
- 금지: box-shadow, 8px radius, 3D, gradient, 네온, 임의 색상
- 레이아웃: sidebar_wrap(kws, text) → chart는 밖에
- 폰트: Noto Sans KR, tabular-nums
```

### 24-2. 종목별 변경 요소 (config.py만 수정)

```
TICKER, COMPANY_NAME, COMPANY_NAME_EN
SUBTITLE (캐치프레이즈)
PEERS_KR, PEERS_GLOBAL
TEAM_NAME, TEAM_MEMBERS
Key Chart 4개 선택
Glossary 용어 10~15개
섹션별 본문 내용
```

### 24-3. 품질 체크포인트

빌드 완료 후 자동 검증:

```python
# QUALITY_CHECKLIST — HARD_MIN(9-4b) 통과 후 우수 등급 달성 기준
# ※ HARD_MIN과 중복 항목 제거 완료. 여기는 HARD_MIN 초과분만 기재.
QUALITY_CHECKLIST = {
    # === 우수 등급 (HARD_MIN 60K 초과) ===
    "min_char_count": 75000,        # 본문 75,000자+ (HARD_MIN: 60K 필수)
    # === Evaluator 심화 검증 ===
    "scenario_tp": True,            # 확률 가중 TP 존재?
    "implied_per_check": True,      # Implied PER sanity check?
    "cfs_appendix": True,           # 연결 IS/BS/CF?
    "ofs_appendix": True,           # 별도 IS/BS/CF?
    "source_per_chart": True,       # 모든 차트에 출처?
    "multiple_basis": True,         # 멀티플 기준 시점 명시? (Forward/Trailing/12MF)
    "design_consistency": True,     # 퍼플 테마 + SMIC 레이아웃?
    # === 서술 품질 ===
    "no_bimon": True,               # 비문 0개? (주어-서술어 불일치, 조사 오류, 번역투)
    "no_filler": True,              # 공허한 문장 0개? (출처 없는 주장, 일반론, 중복)
    "paragraph_uniformity": True,   # 문단 길이 균일? (200~400자, σ<200)
    "data_consistency": True,       # 수치 일관성? (표지/본문/sidebar/Appendix 동일)
    "no_past_tense_spam": True,     # "~하였다" 과거형 5회 이하?
    "no_textbook_defs": True,       # Appendix 교과서 정의 0건?
    # === 시각화 심화 ===
    "chart_y_zero_bar": True,       # 막대그래프 Y축 0 시작?
    "chart_est_hatching": True,     # 추정치(E) 빗금 패턴 구분?
    "chart_heatmap_numbers": True,  # 히트맵 셀에 숫자 표시?
    "chart_min_fontsize": True,     # SVG 텍스트 최소 11px?
    "chart_no_3d": True,            # 3D 차트 0건?
    "chart_dual_axis_label": True,  # 이중축 (좌)/(우) 명시?
}

## 28. 시각화 규칙집 (v9, 딥 리서치 기반)

Tufte/Few/Knaflic + 증권사 관행 + 색맹 대응 종합. **모든 차트 생성 시 이 규칙 준수 필수.**

### 25-1. Y축 스케일 (가장 중요한 규칙)

| 차트 유형 | Y축 0 시작 | 예외 | 이유 |
|-----------|:---------:|------|------|
| 수직/수평 막대 | **필수** | 없음 | 막대 길이 = 값의 크기. 절단하면 비율 왜곡 |
| 라인 차트 | 권장 | 변동폭 좁으면 절단 허용 (시작점 명시 필수) | 추세(기울기)가 핵심 |
| 산점도 | 불필요 | 데이터 범위에 맞추면 됨 | 점의 위치 관계가 핵심 |

```python
# 막대그래프: Y축 0 강제
y_min = 0
y_max = max(values) * 1.15  # 상단 15% 여유 (라벨 공간)

# 라인 차트: 데이터 범위 기반
data_range = max(values) - min(values)
y_min = min(values) - data_range * 0.1
y_max = max(values) + data_range * 0.1
```

### 25-2. 추정치(E) vs 실적(A) 시각 구분 (필수)

**현재 문제**: 추정치와 실적이 동일한 색/스타일로 표시 → 독자가 구분 불가.

```
실적(A): 불투명 100%, 실선
추정(E): alpha 0.4 + 빗금 패턴(SVG hatching) + 대시 라인

SVG 빗금 패턴:
<defs>
  <pattern id="est-hatch" patternUnits="userSpaceOnUse" width="6" height="6">
    <path d="M0,6 L6,0" stroke="#7c6af7" stroke-width="1.5" opacity="0.6"/>
  </pattern>
</defs>
```

### 25-3. 차트 유형 선택 가이드

| 보여주려는 것 | 최적 차트 | 금지 |
|-------------|----------|------|
| 연도별 매출 (≤6개) | 수직 막대 | 파이 |
| 분기별 추이 (7+) | 라인 | 파이 |
| 매출 구성비 (3~5) | 도넛 | 3D 파이 |
| 매출+OPM 동시 | 이중축 (bar+line) | 이중 라인 |
| Peer OPM vs PER | 산점도 | 막대 |
| 비용 분해 | 워터폴 | 파이 |
| DCF 민감도 | 히트맵 (숫자 필수) | 막대 |
| 밸류에이션 범위 | Football Field | 라인 |
| PER/PBR Band | 밴드 차트 | 막대 |
| 주가 1년 일봉 | 라인 (fill) + 거래량 바 | 막대 |

### 25-4. 절대 금지 패턴

1. **3D 차트** → 원근법이 값 왜곡
2. **파이 차트 6개+ 슬라이스** → 수평 막대로
3. **축 라벨 누락** → Y축 단위, X축 기간 필수
4. **범례를 차트 밖 먼 곳에** → 직접 라벨(라인 끝에 이름)
5. **X축 그리드** → Y축 그리드만 유지
6. **무지개 색상** → 의미 기반 색상만
7. **세로 X축 라벨** → 수평 막대로 전환
8. **그라데이션 막대** → 단색이 정확
9. **이중축 라인-라인** → Small multiples로 대체
10. **chartjunk** (그림자, 3D, 아이콘 장식)

### 25-5. 색맹 대응 (필수)

- 빨강-초록 조합 사용 시 **패턴/마커 추가** (남성 8% 색각 이상)
- 히트맵: **셀에 반드시 숫자 값 표시** (색상만으로 전달 금지)
- 라인 차트: **대시 패턴 병용** (실선/대시/점선)
- Positive=#4ecdc4(틸), Negative=#ff6b6b(레드) → 명도 차이로 구분 가능

### 25-6. SVG 텍스트 크기 (하한 규칙)

| 요소 | 최소 | 권장 |
|------|------|------|
| 차트 제목 | 14px | 16px |
| 축 라벨/눈금 | 11px | 12px |
| 데이터 라벨 | 10px | 11px |
| 출처 | 9px | 10px |
| **절대 하한** | **9px** | 이 이하 금지 |

**기존 matplotlib labelsize=8 → 11로 상향 필수.**

### 25-7. 이중축 차트 규칙

매출+OPM 조합만 허용. 필수 5가지:
1. 막대 = 좌축, 라인 = 우축 (역전 금지)
2. 좌축 0 시작 (막대)
3. 우축 라벨에 "(%) (우)" 명시
4. 색상 완전 분리: 막대=Primary, 라인=Negative or Secondary
5. 범례에 "(좌)" "(우)" 명시

### 25-8. 단위 표기 규칙

| 규모 | 단위 | 예시 |
|------|------|------|
| ~9.9억 | 억원 | "영업이익 523억원" |
| 10억~9,999억 | 십억원 | "매출 1,523십억원" |
| 1조+ | 조원 | "매출 22.1조원" |

Y축 상단 or 차트 제목 우측에 `(단위: 십억원)` 표기. 단위 없는 숫자 금지.

### 25-9. 기간 표기 + 추정 구분

```
실적: 2023A, 2024A, 2025A (A = Actual, 불투명 100%)
추정: 2026E, 2027E, 2028E (E = Estimate, alpha 0.4 + 빗금)
```

### 25-10. viewBox 반응형 설정

```html
<svg viewBox="0 0 700 400"
     style="width:100%; max-width:700px; height:auto;">
<!-- width/height 속성 제거, CSS로 제어 -->
<!-- 종횡비 7:4 권장 -->
```

### 25-11. 차트별 구현 규칙 (증권사 표준)

**매출/OPM 이중축**: 좌축=매출 막대(퍼플), 우축=OPM 라인(레드, 마커). 실적=불투명, 추정=빗금.
**PER Band**: 주가 굵은 실선 + PER Nx 밴드 얇은 점선. 현재 위치 강조.
**Football Field**: Low~High 수평 바 + 현재가 수직 점선(레드) + 목표가 수직 실선(퍼플).
**민감도 히트맵**: 셀에 숫자 필수 + Base case 두꺼운 테두리 + 틸-회색-레드 그라데이션.
**워터폴**: 막대 간 연결선 필수 + 각 막대 위 절대값 + 아래 매출 대비 %.

### 25-12. 참고 문헌

- Tufte "The Visual Display of Quantitative Information" (1983/2001)
- Stephen Few "Show Me the Numbers" (2004/2012)
- Cole Nussbaumer Knaflic "Storytelling with Data" (2015)
- Correll "Truncating the Y-Axis" (2019)
- Datawrapper Academy: Y축/이중축/색맹 가이드
```

Evaluator가 이 체크리스트를 자동 검증. 미달 항목이 있으면 구체적 수정 지시 후 재빌드.


## 29. v10 패치노트 — KSS해운 실전 빌드 교훈 (2026.03.28)

KSS해운(044450) 보고서 빌드 과정에서 발견한 문제와 해결책을 스킬에 반영.

### 29-1. 서브에이전트 병렬 빌드 패턴 (필수)

**문제**: 단일 에이전트가 60,000자+ 본문 + SVG 50개 + 테이블 25개를 한 번에 작성하기 불가능. 컨텍스트 한계와 시간 소요.

**해결**: 파일 분리 구조 + 서브에이전트 5개 병렬 실행.

```
cufa_report_{종목코드}/
├── build_{종목명}.py          # 메인: import + 조립 + HARD_MIN 검증
├── build_template.py          # 로컬 포크 (헬퍼 함수, CSS, JS)
├── sections/
│   ├── __init__.py
│   ├── config.py              # 종목 데이터 (재무, Peer, WACC, 시나리오)
│   ├── cover.py               # 표지/TOC/Key Charts/용어/주가분석/Key Debates/VP
│   ├── industry.py            # 섹션1 기업개요 + 섹션2 산업분석 + 섹션2-1 기업분석
│   ├── thesis.py              # 섹션3~5 투자포인트 ①②③
│   ├── financial.py           # 섹션6 재무 + 섹션7 Peer + 섹션8 추정 + 섹션9 밸류
│   └── appendix.py            # 섹션10 리스크 + 섹션11 Appendix + Compliance + Footer
├── output/
│   └── {종목명}_CUFA_보고서.html
└── data/
```

**에이전트 실행 순서**:
1. 메인 에이전트: config.py 작성 (모든 데이터 정의) + build_{종목명}.py 작성 (조립 로직)
2. 서브에이전트 5개 병렬: cover.py, industry.py, thesis.py, financial.py, appendix.py 동시 작성
3. 메인 에이전트: 빌드 실행 + HARD_MIN 검증 + 문제 수정

**핵심 규칙**:
- 각 서브에이전트는 **자기 파일만 Write** — 다른 파일 수정 금지
- 모든 데이터는 **config.py에서 import** — 서브에이전트 간 데이터 불일치 방지
- build_template.py 헬퍼는 **공유 import** — SVG/테이블/레이아웃 함수 재사용
- 서브에이전트에 **정확한 분량 목표** 전달 (섹션별 최소 자수)

### 29-2. SVG 차트 품질 규칙 (v10 강화)

**문제**: SVG 차트가 너무 크고, 텍스트가 겹치고, 데이터 값이 안 보이고, 막대 높이 차이가 안 남.

**해결 — build_template.py 수정사항**:

#### 차트 크기 표준 (v10)
| 차트 유형 | width | height | 비고 |
|---------|-------|--------|------|
| svg_bar, svg_line | 600 | 260 | 기존 700x300에서 축소 |
| svg_donut | 360 | 300 | 기존 420x340에서 축소 |
| svg_waterfall | 600 | 350 | 기존 700x500에서 축소 |
| svg_scatter | 500 | 350 | 기존 600x400에서 축소 |
| svg_football | 600 | auto | 축소 |
| svg_heatmap | 550 | auto | 축소 |
| ~~svg_radar~~ | ~~400~~ | ~~400~~ | **삭제 (v13)** — 레이더 차트 절대 금지 |

#### auto_base — 막대그래프 Y축 자동 조정
```python
# svg_bar에 auto_base=True 파라미터 추가
# 데이터 최소값이 최대값의 30% 이상이면 Y축을 0이 아닌 최소값*70%에서 시작
if auto_base and min(values) > 0 and min(values) / max(values) > 0.3:
    y_base = min(values) * 0.7
else:
    y_base = 0
```
이렇게 하면 매출 2,262~5,614 같은 데이터에서 막대 높이 차이가 잘 보임.

#### 라인 차트 데이터 값 표시
svg_line의 각 포인트 중 **첫번째, 마지막, 최대, 최소**에 값 텍스트 자동 표시.

#### 텍스트 겹침 방지
- 막대 위 값: y 오프셋 -8 (기존 -6)
- X축 라벨 5자 초과 시 font-size 9px
- 바 너비: `min(40, gap * 0.55)` (기존 50, 0.6)
- 도넛: 5% 미만 슬라이스 라벨 생략
- **SVG 내 모든 텍스트는 겹치지 않도록 위치 계산 필수**

#### CSS chart-box (v10)
```css
.chart-box { padding:12px; max-width:600px; margin:0 auto; }
.chart-box svg { max-height:300px; }
.chart-pair .chart-box { max-width:none; }  /* pair 안에서는 해제 */
```

### 29-3. add_source 중복 방지 (CRITICAL)

**문제**: `chart_with_context(pre, chart, post)` + `add_source(chart)` 조합 시 동일 차트가 2번 출력됨. KSS해운에서 **20개 중복 차트** 발생.

**원인**: `chart_with_context`가 chart HTML을 출력하고, `add_source`도 chart HTML을 다시 출력.

**해결 — 절대 규칙**:
```python
# ✅ 올바른 패턴: add_source를 먼저 적용 → chart_with_context에 전달
chart = add_source(svg_bar(...), "출처: DART")
h += chart_with_context(pre, chart, post)

# ❌ 금지 패턴: chart_with_context 후 add_source 별도 추가
chart = svg_bar(...)
h += chart_with_context(pre, chart, post)
h += add_source(chart, "출처")  # ← 이러면 차트 2번 나옴!
```

**Evaluator 자동 검증 추가**:
```python
# 빌드 후 중복 SVG 검사
svg_titles = re.findall(r'class="chart-title">(.+?)</div>', html)
duplicates = [t for t in svg_titles if svg_titles.count(t) > 1]
if duplicates:
    print(f"  [WARN] 중복 도표: {set(duplicates)}")
```

### 29-3b. Post-processing 수치 치환 — 보호-치환-복원 패턴 (v14.2, 2026.04.11 현대건설 교훈)

**핵심 원칙**: 본문에 **광범위 치환(`'45,000원' → '200,000원'` 등)을 적용할 때 반드시 v1 참조 블록을 보호해야 한다.** 그렇지 않으면 `"v1 BUY 45,000원이 v2 HOLD 200,000원으로 하향"` 같은 비교 문구가 `"v1 BUY 200,000원이 v2 HOLD 200,000원"`으로 망가진다.

#### 실전 교훈 (현대건설 v2 Re-rating 세션)

주가가 1년 +370% 급등한 종목의 v2 재평가 시, 다음 치환 규칙을 적용했다:
```python
v2_number_map = [
    ('33,500원', '179,500원'),
    ('45,000원', '200,000원'),
    ('+34.3%', '+11.4%'),
    ('Risk/Reward 6.14', 'Risk/Reward 1.03'),
    ...
]
```

결과: `Re-rating Note v2` 블록의 v1 설명 문구가 자기 자신을 가리키는 모순이 발생:
- `"v1 보고서의 '현재가 33,500원 · 목표 45,000원 · BUY'는 구식"` → `"현재가 179,500원 · 목표 200,000원 · BUY"` (동일 값, 의미 상실)
- `"v1 BUY 45,000원이 v2 HOLD 200,000원"` → `"v1 BUY 200,000원이 v2 HOLD 200,000원"` (논리 붕괴)

#### 해결: Private Use Area 마커 기반 보호-치환-복원

```python
def smic_style_inject_v2_numbers(html):
    import re as _re
    MARKER_V2_S = '\uE100'  # Private Use Area Start
    MARKER_V2_E = '\uE101'  # Private Use Area End
    v2_protected = []

    def v2_protect(m):
        v2_protected.append(m.group(0))
        return f'{MARKER_V2_S}{len(v2_protected)-1}{MARKER_V2_E}'

    # 1) 보호 영역: v1 참조를 포함하는 모든 블록
    protect_patterns = [
        # Re-rating v2 섹션 전체 (v1 비교 테이블, v1 설명 문구 포함)
        r'<div class="section" id="rerating_v2".*?(?=<div class="section"|<div class="footer")',
        # Phase 6.5 백테스트 블록
        r'<div class="section" id="phase65".*?(?=<div class="section"|<div class="footer")',
        # Cover 블록 (이미 직접 편집으로 v2 반영됨)
        r'<div class="cover">.*?(?=<div class="section")',
    ]
    for pat in protect_patterns:
        html = _re.sub(pat, v2_protect, html, flags=_re.DOTALL)

    # 2) 치환 — 안전한 유일 리터럴만. 단독 숫자(예: "45,000") 금지
    v2_number_map = [
        # 고유 리터럴 (v1 전용 맥락에서만 등장)
        ('시가총액 3.74조원', '시가총액 20.05조원'),
        ('Trailing PER 5.2배', 'Trailing PER N/A (2024 적자)'),
        ('Target PER 5.3배', 'Target Fwd PER 15.4배'),
        ('Fwd PER 3.9배', 'Fwd PER 15.4배'),
        ('Conviction: HIGH', 'Conviction: MEDIUM'),
        ('확신도를 HIGH', '확신도를 MEDIUM'),
    ]
    # ❌ 금지: ('45,000원', '200,000원') — 광범위 단독 숫자
    # ❌ 금지: ('33,500', '179,500') — 백엔드 날짜·테이블 셀과 충돌 위험
    # ✅ 대안: 섹션별 직접 Edit으로 핀포인트 교체
    for old, new in v2_number_map:
        html = html.replace(old, new)

    # 3) 복원
    html = _re.sub(f'{MARKER_V2_S}(\\d+){MARKER_V2_E}',
                   lambda m: v2_protected[int(m.group(1))], html)
    return html
```

#### 금지 규칙

| 치환 규칙 유형 | 예시 | 판정 |
|---|---|---|
| 고유 리터럴 (v1 전용) | `'시가총액 3.74조원' → '시가총액 20.05조원'` | ✅ 안전 |
| 고유 맥락 (전후 단어 포함) | `'Trailing PER 5.2배' → '...N/A'` | ✅ 안전 |
| 단독 숫자 | `'45,000원' → '200,000원'` | ❌ 금지 |
| 일반 용어 | `'BUY' → 'HOLD'` | ❌ 금지 (컨센서스/v1 참조에도 등장) |
| 퍼센트 | `'+34.3%' → '+11.4%'` | ⚠ 위험 (우연 일치 가능) |

#### 판단 기준

**단독 숫자나 일반 용어를 치환하고 싶다면, 그 표현이 "v1 참조 블록 밖"에서만 등장하는지 grep으로 먼저 확인.** 2곳 이상 다른 맥락에 등장하면 광범위 치환 대신 **섹션별 직접 Edit**으로 처리.

#### v1 참조 잔재는 "의도적 교훈"으로 유지

치환 이후에도 "v1 시점 주가 33,500원", "v1 BUY 45,000원" 같은 문구는 **의도적으로 남겨둔다**. 이는 CUFA 리서치의 "반증 가능성" 원칙 구현이며, 독자가 "왜 v1이 틀렸는지" 추적 가능하게 하는 학술 연구의 핵심 가치이다.

### 29-4. 이미지 사용 규칙 (v10, 외부 URL 허용)

**기존 규칙**: "외부 CDN/라이브러리 일체 금지"
**v10 변경**: **기업 공식 홈페이지 이미지 + Google Fonts는 허용**

#### 이미지 수집 우선순위
1. **해당 기업 공식 홈페이지** — 로고, 선박/공장/제품 이미지 (최우선)
2. **DART IR 자료** — 기업 제공 공식 이미지
3. **Wikimedia Commons** — CC 라이센스 이미지 (출처 명시)
4. **절대 금지**: Unsplash/Pexels 등 스톡 이미지 (기업과 무관한 이미지 위험)

#### 이미지 수집 절차
```
1. WebFetch로 기업 홈페이지 접속 → img src URL 추출
2. 로고 + 대표 이미지(제품/선박/공장) 2~3개 선별
3. URL 직접 사용 (다운로드 불필요, hotlink)
4. 표지 배너, 산업분석, 기업분석에 배치
5. 캡션에 "(출처: {기업명} 홈페이지)" 명시
```

#### CSS 클래스
```css
.report-img { max-width:100%; height:auto; border-radius:4px; margin:12px 0; }
.logo-img { height:40px; width:auto; }
```

### 29-5. Float TOC 본문 겹침 방지 (v10)

**문제**: `.report` max-width 1100px + `.float-toc` right:20px 조합에서 화면 1200~1400px일 때 겹침.

**해결**:
```css
.report { max-width:960px; }
.float-toc { right: max(12px, calc((100vw - 960px)/2 - 195px)); width:170px; backdrop-filter:blur(6px); border:1px solid var(--border); }
@media (max-width:1400px) { .float-toc, .section-dots { display:none; } }
```

### 29-6. 레이더 차트 — 완전 금지 (v13)

**v13 확정: svg_radar() 완전 삭제. 레이더/스파이더 차트는 어떤 상황에서도 사용하지 않는다.**
- 근거: feedback_no_radar.md ("레이더/스파이더 차트 절대 금지")
- 대안 ①: Peer 비교 → `svg_grouped_bar()` 또는 `table()` (정량 데이터 더 명확)
- 대안 ②: 정성 평가 → **Management Scorecard 테이블** (각 항목에 정량 근거 1줄 필수)
- 대안 ③: 다차원 비교 → `svg_scatter()` (OPM vs PER) 또는 `svg_heatmap()`

### 29-7. expand_card 사용 가이드

**문제**: 핵심 투자 논거가 expand_card 안에 접혀있으면 독자가 놓침.

**규칙**:
- ✅ expand_card 적합: 연혁, 생산거점 상세, Appendix 테이블, 부가 설명
- ❌ expand_card 부적합: 투자포인트 근거, 핵심 재무 분석, 밸류에이션 논리
- **핵심 정보는 항상 펼쳐진 상태로** — 클릭해야 보이는 정보는 안 본다고 가정

### 29-8. 서브에이전트 프롬프트 체크리스트

서브에이전트에게 섹션 작성을 맡길 때 반드시 전달할 항목:
```
□ config.py import 경로 (sys.path 설정)
□ 사용 가능한 헬퍼 함수 목록
□ 해당 섹션 최소 자수
□ 필수 SVG 차트 수 + 유형
□ counter_arg 필요 여부
□ chart_with_context 사용 필수 (add_source 별도 호출 금지!)
□ sidebar_wrap 키워드 최소 개수
□ 서술 규칙 (단정체, 출처, data_tip)
□ config.py에서 사용할 데이터 변수명
□ 이미지 사용 시 기업 홈페이지 URL만
#   □ v12 SMIC 문체: '동사' 지칭 (커버 첫 등장 제외)
#   □ v12 볼드-첫문장: 모든 단락 첫 문장 <strong> 처리
#   □ v12 '본서는': 보고서 주장 시 "본서는~판단한다" 패턴
#   □ v12 '전술한/후술할': 섹션 간 크로스레퍼런스 2회+
#   □ v12 인라인 반박: IP당 1건 (본문 내 "다만/그러나" 패턴)
#   □ v12 과거 사이클: IP 1건 이상에 유사 과거 시점 비교 테이블
#   □ v12 Target Multiple 3단계: 역사적 밴드 + Peer 평균 + 프리미엄 근거
#   □ v12 캐치프레이즈: 섹션 제목에 은유/질문/패러디형 부제
#   □ v12 국가별 비교: 산업분석에 미국/중국/유럽/일본 각 2~3단락
#   □ v12 "보수적 가정에서도": 밸류에이션 결론에 Bear case 하방 명시
```

## 30-0. PRE-FLIGHT CHECKLIST — 보고서 작성 시작 전 표준 선행 검증 (v14.2, 2026.04.11 신설)

**🚨 이 표준 프로토콜을 통과하지 않으면 어떤 섹션도 작성을 시작하지 말 것.** 본 체크리스트는 **종목 독립형 표준 프로토콜**이며, 입력값(config)만 바꾸면 모든 종목에 동일하게 적용된다. 수치·임계값·대응 매트릭스는 전부 상수로 정의되어 있어 종목별 하드코딩이 필요 없다.

### 30-0-1. 표준 임계값 상수 (TOLERANCE CONSTANTS)

```python
# preflight/thresholds.py — 모든 종목에 동일 적용
from dataclasses import dataclass

@dataclass(frozen=True)
class PreflightThresholds:
    # 재무 검증
    FINANCIAL_DRIFT_MAX: float = 0.10        # 빌더 vs 실데이터 괴리 한계 (10%)
    OP_INCOME_SIGN_CHECK: bool = True        # 영업손익 부호 반전은 무조건 STOP

    # 주가 검증
    PRICE_DRIFT_MAX: float = 0.10            # 현재가 vs 빌더 괴리 한계 (10%)
    VOLATILITY_RERATING_TRIGGER: float = 0.30  # 1년 수익률 ±30% 초과 시 Re-rating Note 모드

    # 삼각검증
    TRIPLE_CHECK_TOLERANCE: float = 0.20     # PBR×BPS ≈ 현재가 허용 오차 (20%)
    SELF_CONSISTENCY_TOLERANCE: float = 0.01 # PBR × BPS = Price 자체 정합성 (1%)

    # 데이터 품질
    MIN_YEARS_ACTUAL: int = 3                # 최소 실적 연도
    MIN_DAYS_OHLCV: int = 200                # 최소 주가 거래일 수
    REQUIRE_RAW_ARCHIVE: bool = True         # data/raw/ 원본 보존 필수

THRESHOLDS = PreflightThresholds()
```

**모든 종목에서 이 상수를 import하여 사용.** 종목별로 임계값을 바꾸려면 `PreflightThresholds`를 상속해서 오버라이드.

### 30-0-2. 5점 표준 체크 프로토콜

```
[표준 Pre-flight 체크 — 종목 무관]

□ ① 재무제표 실시간 검증 [CRITICAL]
   Input : config.STOCK_CODE, config.TARGET_YEAR
   Action: MCP dart_financial_statements 실호출
   Check : 매출/영업이익/순이익 최근 N년(≥ MIN_YEARS_ACTUAL)
   Fail  : |builder - actual| / actual > FINANCIAL_DRIFT_MAX → STOP
   Fail  : sign(builder_op) ≠ sign(actual_op) → STOP (부호 반전)

□ ② 주가 실시간 검증 [CRITICAL]
   Input : config.STOCK_CODE
   Action: MCP stocks_history 실호출 (start=today-365, end=today)
   Check : 거래일 수 ≥ MIN_DAYS_OHLCV, 현재가 = 최근 종가
   Fail  : |builder_price - actual_price| / actual > PRICE_DRIFT_MAX → STOP
   Flag  : 1년 수익률 절대값 > VOLATILITY_RERATING_TRIGGER → Re-rating Mode

□ ③ 삼각검증 (PBR·BPS·Price 정합성) [CRITICAL]
   Check : PBR = Price / BPS 가 config 내부 정합적인가?
           시총 = Price × 발행주식수 가 config와 일치하는가?
           Fwd PER = Price / EPS_next 가 config와 일치하는가?
   Fail  : 1개라도 > SELF_CONSISTENCY_TOLERANCE → STOP

□ ④ 원본 응답 파일 보존 [MANDATORY]
   Action: MCP 응답 원본을 data/raw/{stock_code}_{tool}_{YYYYMMDD}.raw 로 저장
   Check : REQUIRE_RAW_ARCHIVE == True 시 파일 존재 필수
   Fail  : 파일 없음 → 재수집 강제

□ ⑤ 산업 특이 체크리스트 로드
   Input : config.INDUSTRY (enum)
   Action: INDUSTRY_CHECKLIST[industry] 조회 → 산업별 필수 데이터 확인
   Fail  : 해당 산업 체크리스트에 정의된 필수 항목 누락 → 2차 MCP 수집
```

### 30-0-3. 실패 대응 매트릭스 (표준)

| Fail Code | Trigger 조건 | 표준 대응 |
|---|---|---|
| `F1_FINANCIAL_DRIFT` | 재무 ±FINANCIAL_DRIFT_MAX 초과 | 빌더 수치 → MCP 실데이터 교체, config.py 재작성, 본문 논지 재검토 |
| `F1_SIGN_FLIP` | 영업손익 부호 반전 | **Kitchen Sinking vs 실적 악화 판정** (섹션 30-2a), 섹션6 적자 해설 블록 추가 |
| `F2_PRICE_DRIFT` | 주가 ±PRICE_DRIFT_MAX 초과 | 현재가 갱신, 모든 상대지표(Upside, Risk/Reward) 재계산 |
| `F2_VOLATILITY` | 1년 수익률 ±VOLATILITY_RERATING_TRIGGER 초과 | **Re-rating Note v2 모드** 전환 (섹션 31-13), 기존 섹션은 v1 참조로 보존 |
| `F3_TRIPLE_CHECK` | PBR×BPS ≠ Price | config.py 수치 재검증, builder.py 상수 재입력 |
| `F4_RAW_MISSING` | 원본 응답 미보존 | 즉시 MCP 재호출 + 저장. 재호출 불가 시 "데이터출처" 시트에 응답 시각 명시 |
| `F5_INDUSTRY` | 산업 체크리스트 항목 누락 | 섹션 30-2 INDUSTRY_CHECKLIST 기준 2차 MCP 호출 |

### 30-0-4. 표준 구현 모듈 (preflight/checker.py)

```python
# preflight/checker.py — 모든 종목에 재사용
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .thresholds import THRESHOLDS


class MCPClient(Protocol):
    """Nexus MCP 클라이언트 인터페이스 (의존성 주입용)"""
    def call(self, tool_name: str, arguments: dict) -> dict: ...


@dataclass(frozen=True)
class PreflightConfig:
    """종목별 config (종목 독립, 값만 주입)"""
    stock_code: str           # "000720"
    target_year: int          # 2024
    industry: str             # "건설" / "해운" / ...
    builder_revenue: float    # 빌더 하드코딩 매출
    builder_op_income: float  # 빌더 하드코딩 영업이익
    builder_price: float      # 빌더 하드코딩 현재가
    builder_bps: float        # 빌더 하드코딩 BPS
    builder_eps_next: float   # 빌더 하드코딩 2026E EPS
    shares_outstanding: float # 발행주식수
    data_dir: Path            # data/raw/ 경로


@dataclass(frozen=True)
class PreflightResult:
    """Pre-flight 결과 — 구조화된 fail code 반환"""
    passed: bool
    fails: tuple[str, ...]    # ("F1_FINANCIAL_DRIFT", "F2_VOLATILITY")
    actual_price: float | None
    actual_revenue: float | None
    actual_op_income: float | None
    one_year_return: float | None


def preflight_validate(config: PreflightConfig, mcp: MCPClient) -> PreflightResult:
    """표준 Pre-flight 검증 — 종목 무관"""
    fails: list[str] = []

    # ① 재무 검증
    dart_resp = mcp.call("dart_financial_statements", {
        "stock_code": config.stock_code,
        "year": str(config.target_year),
        "report_type": "CFS",
    })
    actual_rev, actual_op = _parse_dart_is(dart_resp)
    if abs(config.builder_revenue - actual_rev) / actual_rev > THRESHOLDS.FINANCIAL_DRIFT_MAX:
        fails.append("F1_FINANCIAL_DRIFT")
    if THRESHOLDS.OP_INCOME_SIGN_CHECK and (config.builder_op_income * actual_op < 0):
        fails.append("F1_SIGN_FLIP")

    # ② 주가 검증
    from datetime import date, timedelta
    today = date.today()
    stock_resp = mcp.call("stocks_history", {
        "stock_code": config.stock_code,
        "start_date": (today - timedelta(days=365)).isoformat(),
        "end_date": today.isoformat(),
    })
    actual_price, year_return = _parse_ohlcv(stock_resp)
    if abs(config.builder_price - actual_price) / actual_price > THRESHOLDS.PRICE_DRIFT_MAX:
        fails.append("F2_PRICE_DRIFT")
    if abs(year_return) > THRESHOLDS.VOLATILITY_RERATING_TRIGGER:
        fails.append("F2_VOLATILITY")  # Flag → Re-rating Mode

    # ③ 삼각검증
    implied_pbr = config.builder_price / config.builder_bps
    if abs(implied_pbr * config.builder_bps - config.builder_price) / config.builder_price > THRESHOLDS.SELF_CONSISTENCY_TOLERANCE:
        fails.append("F3_TRIPLE_CHECK")

    # ④ 원본 보존
    if THRESHOLDS.REQUIRE_RAW_ARCHIVE:
        dart_raw = config.data_dir / f"{config.stock_code}_dart_{today:%Y%m%d}.raw"
        stock_raw = config.data_dir / f"{config.stock_code}_stock_{today:%Y%m%d}.raw"
        if not dart_raw.exists() or not stock_raw.exists():
            fails.append("F4_RAW_MISSING")

    # ⑤ 산업 체크리스트
    from .industry_checklist import INDUSTRY_CHECKLIST
    if config.industry not in INDUSTRY_CHECKLIST:
        fails.append("F5_INDUSTRY")

    return PreflightResult(
        passed=len(fails) == 0,
        fails=tuple(fails),
        actual_price=actual_price,
        actual_revenue=actual_rev,
        actual_op_income=actual_op,
        one_year_return=year_return,
    )
```

**사용법** — 모든 빌더의 최상단에 강제 호출:
```python
# build_{종목}.py
from preflight.checker import PreflightConfig, preflight_validate
from preflight.mcp_client import NexusMCPClient  # 표준 클라이언트

def build():
    config = PreflightConfig(
        stock_code=TICKER,
        target_year=REPORT_YEAR - 1,
        industry=INDUSTRY,
        builder_revenue=IS_REVENUE_2024,
        builder_op_income=IS_OP_INCOME_2024,
        builder_price=CURRENT_PRICE,
        builder_bps=BPS_2024,
        builder_eps_next=EPS_2026E,
        shares_outstanding=SHARES,
        data_dir=Path("data/raw"),
    )
    result = preflight_validate(config, NexusMCPClient())
    if not result.passed:
        # 자동 대응: Re-rating Mode 전환 or STOP
        handle_fails(result.fails, config)
    # 이후 섹션 빌드 진행
```

### 30-0-5. MCP 호출 표준 프로토콜 (curl + Python)

Nexus MCP는 Streamable HTTP이며 **SSE Accept 헤더가 필수**이다. 이를 `preflight/mcp_client.py`로 표준화:

```python
# preflight/mcp_client.py — 재사용 가능한 MCP 클라이언트
import json, re, subprocess
from typing import Any

NEXUS_MCP_URL = "http://62.171.141.206/mcp"
SSE_HEADERS = [
    "-H", "Content-Type: application/json",
    "-H", "Accept: application/json, text/event-stream",
]

class NexusMCPClient:
    def __init__(self, url: str = NEXUS_MCP_URL, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self._call_id = 0

    def call(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        self._call_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._call_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        result = subprocess.run(
            ["curl", "-s", "-m", str(self.timeout), self.url, "-X", "POST",
             *SSE_HEADERS, "-d", json.dumps(payload, ensure_ascii=False)],
            capture_output=True, text=True, encoding="utf-8",
        )
        # SSE 파싱: "event: message\ndata: {...}"
        m = re.search(r"data:\s*(\{.*\})", result.stdout, re.DOTALL)
        if not m:
            raise RuntimeError(f"MCP 응답 파싱 실패: {result.stdout[:500]}")
        data = json.loads(m.group(1))
        if data.get("result", {}).get("isError"):
            err = data["result"]["content"][0]["text"]
            raise RuntimeError(f"MCP 도구 에러: {err[:500]}")
        # content[0].text는 JSON 문자열이므로 한 번 더 파싱
        inner = json.loads(data["result"]["content"][0]["text"])
        return inner
```

### 30-0-6. MCP 도구 스키마 레지스트리 (표준화)

**인자명 오타 방지를 위해 스키마를 별도 레지스트리로 관리.** 이건 종목 무관 고정.

```python
# preflight/tool_schemas.py
TOOL_SCHEMAS = {
    "dart_financial_statements": {
        "required": ["stock_code", "year", "report_type"],
        "hints": {
            "stock_code": "6자리 문자열 (ticker 아님)",
            "year": "문자열 '2024'",
            "report_type": "'CFS' or 'OFS' (대문자)",
        },
        "response_quirks": [
            "IS/BS/CF에 연결+별도 혼재 가능 → ord 필드로 구분",
            "당기순이익(손실) 행은 중복 등장 (보통주 EPS 계산용 + 총계)",
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
```

호출 전 스키마 사전 검증:
```python
def validate_args(tool_name: str, arguments: dict) -> None:
    schema = TOOL_SCHEMAS[tool_name]
    missing = [k for k in schema["required"] if k not in arguments]
    if missing:
        raise ValueError(
            f"{tool_name} 인자 누락: {missing}. 힌트: {schema['hints']}"
        )
```

### 30-0-7. DART 응답 파싱 표준 헬퍼

연결(CFS) + 별도(OFS) 혼재 문제는 **종목 무관하게 재발 가능**하므로 표준 파서로 해결:

```python
# preflight/dart_parser.py
def split_cfs_ofs(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """dart_financial_statements 응답을 연결/별도로 분리.
    sj_div 필터 + ord 순서 기반 (앞쪽=CFS, 뒤쪽=OFS)."""
    def _split_by_sj(sj: str) -> tuple[list, list]:
        rows = sorted(
            [r for r in items if r.get("sj_div") == sj],
            key=lambda x: int(x.get("ord", 0)),
        )
        mid = len(rows) // 2
        return rows[:mid] or rows, rows[mid:] if mid > 0 else []

    cfs, ofs = [], []
    for sj in ("IS", "BS", "CF"):
        c, o = _split_by_sj(sj)
        cfs.extend(c)
        ofs.extend(o)
    return cfs, ofs


def get_account_value(rows: list[dict], account_name: str,
                      period: str = "thstrm") -> int:
    """계정명으로 값 추출. period: thstrm(당기) / frmtrm(전기) / bfefrmtrm(전전기)"""
    for r in rows:
        if r.get("account_nm") == account_name:
            raw = r.get(f"{period}_amount", "0").replace(",", "")
            return int(raw) if raw else 0
    return 0
```

### 30-0-8. 검증된 케이스 아카이브 (부록, v14.2+ 누적)

본 체크리스트의 효용성을 검증한 실전 케이스를 표준 대응과 함께 기록한다. **각 케이스는 "가설-발견-대응"의 3요소**로 구조화되며, 미래 종목 작성 시 참조 가능.

| 케이스 ID | 종목 | 발견 Fail Code | 규모 | 적용된 대응 | 기록 일시 |
|---|---|---|---|---|---|
| CASE-000720-v2 | 현대건설 | F1_SIGN_FLIP, F1_FINANCIAL_DRIFT, F2_VOLATILITY, F3_TRIPLE_CHECK | 재무 +52%, 주가 +370%, 영업손익 부호 반전 | Re-rating Note v2 모드, BUY→HOLD 하향, 섹션5 전면 재작성 | 2026.04.11 |

**케이스 추가 규칙**: 새 종목 작성 중 Pre-flight Fail이 발생하면 CASE-{stock_code}-v{N} 형식으로 이 표에 추가. 규모는 드리프트 %로, 대응은 매트릭스 코드로 기록. 수치 자체는 config.py에 있으므로 여기에 하드코딩하지 않는다.

---

## 30. Phase 0 강화 — DART 사업보고서 정독 + 산업별 필수 항목 (v10, CRITICAL)

### 30-1. DART 사업보고서 정독 (Phase 0 최우선, 건너뛰기 절대 금지)

**문제**: MCP `dart_financial_statements`는 IS/BS/CF 숫자만 제공한다. 사업보고서 본문(사업의 내용, 주요 거래처, 리스크 요인, 경영진 토의 등)은 읽지 않으면 핵심 정보를 놓친다.

**절대 규칙**: 보고서 작성 전 반드시 DART에서 해당 기업의 **사업보고서 본문**을 읽는다.

#### 수집 절차
```
Phase 0-A: DART 사업보고서 정독 (Phase 0의 첫 단계, 데이터 수집보다 먼저)
  1. dart.fss.or.kr에서 최신 사업보고서(11011) + 직전 반기보고서(11012) 검색
  2. 사업보고서 본문에서 반드시 확인할 항목:
     □ "II. 사업의 내용" — 사업부 구조, 주요 제품/서비스, 매출 구성
     □ "주요 거래처" 또는 "매출처" — 화주/고객사 목록 + 매출 비중
     □ "원재료 및 주요 자재" — 원가 구조, 공급처
     □ "사업의 위험 요인" — 기업이 직접 인식하는 리스크
     □ "경영진의 경영 토의(MD&A)" — 전략 방향, 시장 인식
     □ "기타 투자 판단에 필요한 사항" — 소송, 규제, 특이사항
     □ 선대/설비/생산능력 현황 (제조업: CAPA, 해운: 선박 목록, IT: 서버/인프라)
     □ 종속회사 현황 — 해외 법인, 합작사
  3. 수집한 정보를 config.py에 dict로 정리
  4. 사업보고서에서 발견한 핵심 팩트를 투자포인트/리스크에 직접 활용
```

**Evaluator 검증**: "주요 거래처"가 보고서 본문에 1회 이상 언급되지 않으면 경고.

#### 산업별 DART 추가 확인 항목

| 산업 | DART 추가 확인 | 왜? |
|------|-------------|-----|
| **해운** | 선박 목록(선명/선종/톤수/건조연도), 주요 항로, COA 계약 상대방, 화물 유형 | 항로=지정학 리스크 직결 |
| **제조** | 공장 목록/CAPA/가동률, 주요 원재료 공급처, 재고 정책 | CAPA=매출 상한선 |
| **금융** | 여신 포트폴리오, 부실채권비율, 자기자본비율 규제 | 규제=사업 제약 |
| **바이오** | 파이프라인 목록/임상 단계, 허가 일정, 특허 만료 | 파이프라인=기업가치 |
| **IT/플랫폼** | MAU/DAU, 고객 해지율, 클라우드 인프라 비용 | KPI=성장 품질 |
| **건설/조선** | 수주잔고 상세(발주처/금액/기간), 공정률, 원가변동 클레임 | 수주잔고=미래 매출 |

### 30-2. 산업별 필수 분석 항목 자동 체크리스트

**문제**: 해운업인데 항로/거래처/지정학 리스크를 빠뜨림. 산업별로 "반드시 다뤄야 할 항목"이 다른데 스킬에 규칙이 없었음.

**해결**: 산업 식별 → 해당 체크리스트 자동 적용.

```python
# 보고서 작성 전 산업 식별 후 체크리스트 로드
INDUSTRY_CHECKLIST = {
    '해운': [
        '선대 현황 (선명/선종/톤수/건조연도) 테이블',
        '주요 항로 + 항로별 지정학 리스크 (호르무즈/수에즈/홍해/말라카)',
        '현재 진행 중인 지정학 이슈 반영 (전쟁/봉쇄/제재)',
        '주요 거래처/화주 (DART 사업보고서 기반)',
        'COA vs 스팟 비중 + COA 계약 상세',
        '운임 지수 (BDI/Baltic LPG/BCTI 등 해당 지수)',
        '벙커유(연료비) 가격 민감도',
        '선박 발주/인도 스케줄 (공급 사이클)',
        '톤마일 분석 (항로 거리 × 화물량)',
        '항로 지도 SVG or 이미지 (필수)',
    ],
    '제조': [
        '공장/생산거점 목록 + CAPA + 가동률',
        '주요 원재료 + 공급처 + 가격 동향',
        '주요 고객사 매출 비중 (집중도 리스크)',
        '기술 경쟁력 (특허, R&D 투자)',
        '환율 민감도 (수출 비중)',
    ],
    '금융': [
        '여신/자산 포트폴리오 구성',
        'NIM/수수료율 추이',
        '자본적정성 (BIS비율/NCR)',
        '부실채권비율 (NPL ratio)',
        '금리 민감도 분석',
    ],
    '바이오': [
        '파이프라인 전수 목록 (적응증/임상단계/성공확률)',
        '특허 만료 일정',
        'FDA/식약처 허가 타임라인',
        'CMO/CDMO 계약 현황',
        '현금 소진율(Burn Rate) + 자금 조달 필요성',
    ],
    'IT/플랫폼': [
        'MAU/DAU/ARPU 추이',
        '고객 해지율(Churn Rate)',
        'Take Rate 변동',
        '클라우드/인프라 비용 구조',
        '경쟁 플랫폼 대비 포지셔닝',
    ],
    '건설/조선': [
        '수주잔고 상세 (발주처/금액/기간/공정률)',
        '매출인식 타이밍 (공정률 기준)',
        '원가변동 클레임 이력',
        '해외 프로젝트 리스크 (환율/정치)',
        '주택/인프라/플랜트 비중',
    ],
}
```

**적용 방법**:
1. Phase 0에서 종목 업종코드(DART `induty_code`) 확인
2. 해당 산업 체크리스트 로드
3. 서브에이전트 프롬프트에 체크리스트 포함
4. Evaluator에서 체크리스트 항목 존재 여부 자동 검증

### 30-3. 지정학 리스크 자동 반영 (Phase 0, 해운/에너지/무역 필수)

**문제**: 이란-이스라엘 전쟁으로 호르무즈 해협이 봉쇄된 상태인데, 보고서에 충분히 반영 안 됨.

**절대 규칙**: 보고서 작성 시점에 진행 중인 지정학 이슈를 반드시 확인하고 반영한다.

```
Phase 0-B: 지정학 이슈 스캔
  1. news_search로 "호르무즈", "수에즈", "홍해", "후티", "전쟁", "봉쇄", "제재" 검색
  2. 해당 기업 항로와 교차 확인
  3. 영향 시나리오:
     - 항로 봉쇄 시: 매출 영향, 대체 항로, 운임 변동
     - 항로 개방 시: 운임 정상화 속도, 수혜 소멸 시점
  4. 투자포인트 또는 리스크에 반드시 포함
  5. Kill Condition에 지정학 변수 1개 이상 포함
```

### 30-4. 도입부 서사 규칙 (AI스러운 문체 방지)

**문제**: 서브에이전트가 쓴 도입부가 "정보 나열형"으로 AI스럽다. SMIC은 이야기처럼 시작.

**규칙 — 서브에이전트 프롬프트에 필수 포함**:
```
[도입부 서술 규칙]
- 첫 문단은 "이야기"로 시작한다. 숫자나 기업명이 아니라 장면/비유/질문으로.
- 예시 (SMIC S-Oil): "정유업은 '시간의 예술'이다. 원유를 사서 제품을 파는 단순한 구조지만..."
- 예시 (SMIC 파마리서치): "강남의 한 피부과 원장은 리쥬란 시술 예약이 3주 밀렸다고 했다."
- 예시 (SMIC 로보티즈): "2024년 CES에서 가장 많은 관심을 받은 것은 AI도 전기차도 아닌 로봇이었다."
- 금지 패턴: "XXX(종목코드)는 XX업종의 기업으로..." ← AI가 쓰는 전형적 도입
- 금지 패턴: "본 보고서에서는..." ← 메타 서술 금지
- 도입부 비유는 해당 산업의 핵심 특성을 30초 안에 전달해야 한다
```

### 30-5. 기업 홈페이지 이미지 수집 표준 절차

```
1. WebFetch로 기업 홈페이지 메인 페이지 → img src URL 전수 추출
2. 로고 이미지 선별 (보통 header에 위치)
3. 대표 제품/선박/공장 이미지 선별 (보통 메인 배너 또는 사업소개 페이지)
4. URL 유효성 확인 (직접 접근 가능한지)
5. 이미지 품질 확인: 최소 800px 너비 권장
6. 대체 소스: 기업 IR 페이지 > 네이버 증권 종목 페이지 > Wikimedia Commons
7. 절대 금지: Unsplash/Pexels 등 스톡 이미지 (기업과 무관한 이미지 로드 위험)
8. 캡션 필수: "(출처: {기업명} 홈페이지)" 또는 "(출처: DART IR 자료)"
```

### 30-6. 시각 자료 다양성 (SMIC 벤치마크, v10)

**문제**: SVG 바/라인/도넛 차트만 반복 → 시각적으로 단조롭고 AI가 만든 티가 난다. SMIC/증권사 보고서는 차트+사진+지도+다이어그램+인포그래픽이 골고루 섞여있다.

**시각 자료 유형 8가지 (최소 5가지 사용 필수)**:

| 유형 | 설명 | 적용 위치 | 구현 방법 |
|------|------|----------|----------|
| ① **데이터 차트** | 바/라인/도넛/산점도/워터폴 | 재무/추정/밸류 | SVG 헬퍼 함수 |
| ② **기업 사진** | 공장/선박/제품/매장 실물 | 표지, 기업개요, 산업분석 | 기업 홈페이지 img URL |
| ③ **지도** | 항로 지도, 거점 지도, 지역별 매출 | 산업분석, 기업분석 | 인라인 SVG 세계지도 or 외부 이미지 |
| ④ **프로세스 다이어그램** | 밸류체인, 사업 플로우, 시너지 구조 | 기업개요, 투자포인트 | svg_flow_diagram + 인라인 SVG |
| ⑤ **비교 매트릭스** | Peer 비교, 경쟁약물 비교, 기술 비교 | Peer 비교, 산업분석 | HTML table + 색상 코딩 |
| ⑥ **타임라인** | 연혁, 이벤트, 촉매 일정 | 주가분석, 리스크 | svg_timeline |
| ⑦ **인포그래픽 카드** | 핵심 숫자 4~6개 하이라이트 | 표지, 각 섹션 시작 | metric-grid HTML |
| ⑧ **Football Field/밴드** | 밸류에이션 범위, PER/PBR 밴드 | 밸류에이션 | svg_football, svg_line (밴드) |

**Evaluator 검증**: 위 8가지 중 최소 5가지 유형이 보고서에 포함되어야 함. 3가지 이하면 경고.

#### 항로/거점 지도 SVG 패턴 (해운/물류/글로벌 기업 필수)

```python
def svg_world_routes(title, routes, ports, width=700, height=350, sec=0):
    """간략화된 세계지도 + 항로 표시.

    Args:
        routes: [{'from': (x,y), 'to': (x,y), 'color': '#7c6af7', 'label': '중동→한국'}]
        ports: [{'pos': (x,y), 'name': '호르무즈', 'color': '#ff6b6b', 'risk': True}]

    세계지도는 simplified continent outlines (SVG path)로 구현.
    주요 해협(호르무즈/수에즈/말라카)을 빨간 점으로 표시.
    항로를 곡선(quadratic bezier)으로 연결.
    """
    pass  # 구현 필요
```

#### SMIC 보고서에서 배울 시각 자료 패턴

| SMIC 보고서 | 시각 자료 패턴 | 우리 적용 |
|------------|-------------|----------|
| 파마리서치 | 강남언니 앱 스크린샷, 시술 사진, 의사 인터뷰 | 기업 IR 자료 사진 |
| S-Oil | 정유 공정도, 지역별 정제시설 지도 | 밸류체인 플로우 + 거점 지도 |
| 로보티즈 | CES 로봇 사진, 기술 비교 매트릭스 | 제품 사진 + Peer 매트릭스 |
| 애니플러스 | 애니메이션 포스터, IP 파생수익 다이어그램 | 콘텐츠 이미지 + OSMU 플로우 |
| JTC | 여행 상품 사진, 지분구조 타임라인 | 기업 사진 + 지배구조 다이어그램 |

**핵심**: "차트만 있는 보고서"는 AI가 만든 티가 난다. "사진+지도+다이어그램+차트"가 섞여야 사람이 만든 것처럼 보인다.

### 30-7. 서브에이전트 도입부 프롬프트 (AI 문체 방지 보강)

cover.py 서브에이전트에 전달할 도입부 규칙:

```
[CRITICAL: 도입부 서술 방식]

1. 첫 2문장은 "장면 묘사" 또는 "질문"으로 시작한다.
   ✅ "페르시아만의 새벽, 84,000CBM급 가스운반선이 호르무즈 해협을 빠져나간다."
   ✅ "한국이 수입하는 LPG의 70%는 어디서 올까?"
   ❌ "KSS해운(044450)은 LPG 전문 해상운송 기업이다."
   ❌ "본 보고서는 KSS해운의 투자 매력을 분석한다."

2. 3~5문장째에서 "왜 지금 이 기업인가" 연결.
   "호르무즈 해협이 봉쇄된 지금, 이 배가 돈이 되는 이유를 묻는다."

3. 캐치프레이즈는 산업 본질을 비유로 압축.
   ✅ "바다 위의 파이프라인" (해운 = 해상 인프라)
   ✅ "석유의 가벼운 형제가 바다를 건너다" (LPG의 본질)
   ❌ "LPG 해상운송 시장의 성장 기회" (교과서)

4. 산업분석(섹션2) 도입부도 동일 규칙 적용.
   섹션마다 첫 문단은 "장면/비유/질문"으로 시작.
```

## 31. 시각화 표준 — SMIC/YIG 10개 보고서 전수 스캔 결과 (v10)

### 31-1. 시각화 밀도 표준

SMIC/YIG 10개 보고서 평균: **페이지당 0.86~1.06개 도표**. 과다하면 시각 피로, 부족하면 빈약.

**CUFA 기준**:
- 목표: HTML 스크롤 기준 "화면 1.5~2개 분량당 도표 1개"
- 최소: SVG 50개 (HARD_MIN)
- 상한: 80개 초과 시 중복/불필요 검토
#
# ▸ 섹션별 도표/텍스트 비율 (v12, SMIC+CUFA 하이브리드)
#   | 섹션 유형    | 도표:텍스트 | chart-pair 비중 | 전폭 도표 예시 |
#   |-------------|:---------:|:-------------:|-------------|
#   | 산업분석     | 40:60     | 50%           | Value Chain, TAM/SAM |
#   | 기업분석     | 45:55     | 50%           | 주가 이벤트 차트 |
#   | 투자포인트   | 50:50     | 60%           | 핵심 논증 차트 |
#   | 재무분석     | 55:45     | 60%           | DuPont 분해 |
#   | 밸류에이션   | 70:30     | 30%           | Football Field, 민감도 |
#   | Appendix    | 90:10     | 20%           | 재무제표 테이블 |

### 31-2. 주가 차트 표준 (SMIC/YIG 공통 패턴)

**모든 학회 보고서가 동일한 패턴**: 일일 종가 라인 + 이벤트 어노테이션.

```
주가 차트 필수 요소:
1. 일일 종가(daily close) 라인 차트 — 월봉/주봉 금지
2. 이벤트 어노테이션 ①②③④ 번호 + 설명 — 최소 5개 이벤트
3. 이동평균선: 없음 (학회 표준)
4. 거래량 바: 없음 (학회 표준)
5. 기간: 1~3년 (종목 특성에 따라)
6. 옵션: Peer 수정주가 비교 (기준일=100 리베이스)
```

**파마리서치 패턴 (최고 수준)**: 주가(좌축) + 매출액+영업이익(우축) 3중 이중축
**S-Oil 패턴**: 주가(좌축) + 유가(우축) 이중축 + "업사이클/다운사이클" 구간 어노테이션

### 31-3. 2열 병렬 배치 표준

SMIC 파마리서치: **전체 도표의 60%를 2열 병렬 배치**. 페이지 하단에 도표 2개를 나란히.

```html
<div class="chart-pair">
  <div class="chart-box">도표 A</div>
  <div class="chart-box">도표 B</div>
</div>
```

**배치 규칙**:
- 동일 주제의 차트 2개 → 병렬 (예: 매출 추이 + OPM 추이)
- 비교 차트 → 병렬 (예: 국내 vs 해외)
- 단독으로 메시지가 강한 차트 → 1열 (예: Football Field, 민감도 히트맵)
- **목표: 전체 차트의 40~50%를 병렬 배치**

### 31-4. 시각화 유형 확대 (SMIC에서 발견, CUFA 미구현)

| 유형 | 설명 | 우선순위 | 적용 대상 |
|------|------|---------|----------|
| **ROE-PBR 경로분석** | 분기별 ROE-PBR 이동 궤적 (화살표 경로) | HIGH | PBR Valuation 시 |
| **회귀분석 차트** | 산점도 + 회귀선 + R²/방정식 표시 | HIGH | ASP 추정, ROE-PBR 관계 |
| **Peer 수정주가 리베이스** | 기준일=100으로 정규화한 다종목 라인 | HIGH | 주가분석 |
| **M/S 밴드 차트** | 점유율 시나리오별 매출 영역(area) | MEDIUM | 시장점유율 시나리오 |
| **파이프라인 간트차트** | 임상 단계별 수평 바 타임라인 | HIGH | 바이오 종목 |
| **3중 이중축** | 주가+매출+OPM 동시 표시 | MEDIUM | 주가 분석 |

향후 build_template.py에 `svg_roe_pbr_path()`, `svg_regression()`, `svg_rebased_price()`, `svg_gantt()` 추가 예정.

### 31-5. 시각화 배치 순서 표준

각 섹션 내 시각화 배치 순서:

```
1. 섹션 제목 + 사이드바
2. 도입부 서사 (장면/비유)
3. 핵심 주장 (Bold 도입문)
4. 데이터 차트 2개 병렬 (근거 #1, #2)
5. 해설 문단 (chart_with_context post)
6. 추가 근거 텍스트
7. 데이터 차트 1개 단독 (핵심 시각화)
8. 테이블 (상세 데이터)
9. counter_arg (반론 논파)
10. 결론 (밑줄)
11. callout (KEY TAKEAWAY)
```

### 31-6. SMIC vs CUFA 시각화 갭 분석

| 항목 | SMIC | CUFA v10 | 갭 |
|------|------|---------|-----|
| 총 도표 | 28~38개 | 74개 | CUFA 과다 (HTML이라 OK) |
| 2열 병렬 | 60% | 사용 중 | ✅ |
| 주가 차트 | 일봉+이벤트 | 월별 요약 → **일봉으로 교체 필요** | 🔴 |
| 기업 사진 | 1~3장 | 선박 1장 | 추가 필요 |
| 지도 | 1~2장 | 항로 지도 SVG | ✅ |
| ROE-PBR 경로 | 1~3개 | 미구현 | 향후 |
| 회귀분석 | 1~2개 | 미구현 | 향후 |
| 밸류체인 | 1개 | MLA SVG | ✅ |

## 32. 시각화 유형 카탈로그 — 80+ 유형 중 CUFA 적용 가능 목록 (v11)

Tableau Desktop의 80+ 시각화 유형을 기반으로, CUFA 보고서에 SVG/HTML로 구현 가능한 유형을 3단계로 분류.

### Tier 1: 현재 구현 완료 (18종 SVG 헬퍼)

| # | 유형 | 헬퍼 함수 | 용도 |
|---|------|----------|------|
| 1 | 수직 막대 | `svg_bar()` | 매출/EPS 추이, 연도별 비교 |
| 2 | 수평 막대 | `svg_hbar()` | Peer PER 비교, 순위형 |
| 3 | 이중축 (바+라인) | `svg_bar(show_line=True)` | 매출+OPM |
| 4 | 그룹 막대 | `svg_grouped_bar()` | 사업부별 분기 비교 |
| 5 | 라인 차트 | `svg_line()` | 추세, 시계열 |
| 6 | 누적 영역 | `svg_area()` | 구성비 추이 |
| 7 | 도넛 차트 | `svg_donut()` | 비중/구성 |
| 8 | 산점도 | `svg_scatter()` | OPM vs PER, 상관관계 |
| 9 | 워터폴 | `svg_waterfall()` | 비용 분해, Bridge |
| 10 | Football Field | `svg_football()` | 밸류에이션 범위 |
| 11 | 히트맵 | `svg_heatmap()` | DCF 민감도 |
| 12 | 버블 리스크 매트릭스 | `svg_bubble_risk()` | 리스크 확률×영향 |
| 13 | 플로우 다이어그램 | `svg_flow_diagram()` | 밸류체인, 프로세스 |
| ~~14~~ | ~~레이더/스파이더~~ | ~~`svg_radar()`~~ | **삭제 (v13)** — grouped_bar/scatter/heatmap으로 대체 |
| 15 | 타임라인 | `svg_timeline()` | 연혁, Catalyst |
| 16 | ROE-PBR 경로 | `svg_roe_pbr_path()` | 밸류에이션 경로분석 |
| 17 | 수정주가 리베이스 | `svg_rebased_price()` | Peer 주가 비교 |
| 18 | 테이블 | `table()` | 재무 데이터, 비교 |

### Tier 2: 구현 예정 (HIGH 우선순위, 금융보고서 필수)

| # | 유형 | 설명 | 적용 대상 |
|---|------|------|----------|
| 19 | **캔들스틱** | OHLC 주가 차트 (네이버 증권 스타일) | 주가 분석 |
| 20 | **박스플롯** | 분기 실적 분포, Peer 분포 비교 | 재무 분석 |
| 21 | **불릿 그래프** | 실적 vs 목표 + 달성도 배경 | KPI 비교 |
| 22 | **간트 차트** | 파이프라인 임상, 프로젝트 일정 | 바이오, 건설 |
| 23 | **Pareto 차트** | 누적 80/20 분석 | 매출 집중도 |
| 24 | **범프 차트** | 순위 변동 추이 | M/S 변동 |
| 25 | **스파크라인** | 미니 인라인 차트 | 테이블 내 추세 |
| 26 | **로리팝 차트** | 얇은 바 + 원 끝점 | 깔끔한 비교 |
| 27 | **코로플레스 지도** | 지역별 색상 매핑 | 지역 매출, 거점 |
| 28 | **히스토그램** | 빈도 분포 | EPS 분포, 운임 분포 |
| 29 | **슬로프 차트** | 두 시점 간 변화 | YoY 비교 |
| 30 | **나비/토네이도** | 양방향 수평 막대 | Bull vs Bear, 민감도 |
| 31 | **트리맵** | 계층적 면적 비중 | 사업부/지역 비중 |
| 32 | **캘린더 히트맵** | 날짜별 색상 | 거래량 패턴 |

### Tier 3: 고급 (LOW 우선순위, 필요시 구현)

| # | 유형 | 설명 | 적용 대상 |
|---|------|------|----------|
| 33 | Sankey 다이어그램 | 플로우 폭 = 크기 | 자금 흐름, 밸류체인 |
| 34 | 코드 다이어그램 | 원형 상호관계 | 거래처 관계 |
| 35 | 선버스트 | 계층적 동심원 | 사업구조 |
| 36 | 와플 차트 | 10×10 격자 비중 | 직관적 비율 |
| 37 | 비스웜/지터 플롯 | 겹침 방지 산점 | 밀집 데이터 |
| 38 | 수평선 차트 | 겹침 영역 | 시계열 비교 |
| 39 | 평행좌표 | 다변수 비교 | Peer 다차원 비교 |
| 40 | Marimekko | 가변폭 적층 | 시장점유율 × 시장규모 |
| 41 | 게이지 차트 | 반원형 달성도 | KPI |
| 42 | 네트워크 다이어그램 | 노드+엣지 | 기업 관계도 |
| 43 | 라디얼 바 | 극좌표 막대 | 시각적 변형 |
| 44 | 스트림 그래프 | 흐르는 누적 영역 | 트렌드 구성비 |
| 45 | 픽토그램 | 아이콘 기반 바 | 직관적 비교 |

### 보고서 유형별 권장 시각화 믹스

| 보고서 유형 | 필수 유형 | 권장 유형 | 최소 종류 |
|------------|----------|----------|----------|
| **기업분석** | 바, 라인, 이중축, 도넛, 산점도, 워터폴, Football, 히트맵, 테이블, 플로우 | 캔들스틱, 불릿, 범프, 스파크라인, 로리팝, 토네이도 | **15종+** |
| **산업보고서** | 바, 라인, 누적영역, 도넛, 산점도, 플로우, 지도, 테이블 | 트리맵, Pareto, Marimekko | **12종+** |
| **바이오** | 바, 라인, 간트, 워터폴, 히트맵, 테이블 | Sankey, 선버스트, 코드 | **10종+** |

### Evaluator 검증

```python
# v11: 보고서 내 시각화 유형 다양성 체크
chart_types_used = set()
if 'svg_bar' in html: chart_types_used.add('bar')
if 'svg_line' in html: chart_types_used.add('line')
if 'svg_donut' in html: chart_types_used.add('donut')
# ... 전수 체크
if len(chart_types_used) < 10:
    print(f'  [WARN] 시각화 유형 {len(chart_types_used)}종 < 10종 최소 기준')
```

### 31-7. sidebar_wrap 레이아웃 규칙 (CRITICAL, v10)

**문제**: sidebar_wrap(키워드 + 본문) 안에 SVG 차트를 넣으면 그리드가 깨진다. 차트 너비가 본문 칼럼을 넘어서 사이드바를 밀어내고, 이후 텍스트도 2열이 아닌 전폭으로 렌더링된다.

**절대 규칙**:
```python
# ✅ 올바른 패턴: sidebar_wrap 안에는 텍스트만. 차트는 바깥에.
h += sidebar_wrap(kws, text_content)   # 텍스트만 (2열 레이아웃 유지)
h += '<div class="chart-pair">\n'       # 차트는 sidebar_wrap 밖
h += chart_a
h += chart_b
h += '</div>\n'

# ❌ 금지 패턴: sidebar_wrap 안에 차트 삽입
content = text + chart_html  # 이러면 그리드 깨짐!
h += sidebar_wrap(kws, content)
```

**배치 순서 (SMIC 표준)**:
1. `sidebar_wrap(kws, 텍스트)` — 사이드바 키워드 + 본문 텍스트
2. `chart-pair` 또는 단독 차트 — sidebar_wrap **밖**에 배치
3. 필요시 추가 `sidebar_wrap` — 차트 해설 텍스트

**chart_with_context 사용 위치**: sidebar_wrap **밖**에서만.

### 31-8. 주가분석 섹션 금지 (v10)

**문제**: SMIC/YIG 어떤 보고서도 "주가분석"이라는 별도 섹션을 두지 않는다. 주가 차트는 표지 또는 기업개요에 소형으로 포함될 뿐.

**규칙**: `gen_stock_analysis()` 같은 별도 섹션 금지. 주가 차트는 표지의 Key Charts 또는 기업개요 섹션에 포함.

### 31-9. Variant Perception 작성 규칙 (v10)

**문제**: "미커버리지 = 시장이 모른다"는 논리적 오류. 증권사 리포트가 없어도 시장 참여자(기관, 개인)는 존재하며 주가에 정보가 반영되어 있다.

**규칙**:
- Variant Perception은 "시장이 모르는 것"이 아니라 "시장이 놓치고 있는 것"
- "미커버리지 → 정보 비대칭"은 VP의 원인일 수 있지만, VP 자체는 아님
- VP는 반드시 **정량적 괴리**로 표현: "시장은 X를 가정하는데 CUFA는 Y로 본다. 이유는 Z"
- ✅ "시장은 성장률 0%를 가정(현재 PER 역산). CUFA는 +6% 추정. 이유: COA 재계약 운임 인상"
- ❌ "시장이 이 기업을 모른다"

### 31-10. 섹션 조립 순서 (v10 확정)

**문제**: Key Debates/VP를 기업개요보다 앞에 놓으면, 기업 소개도 안 했는데 논쟁을 보여주는 비논리적 흐름.

**v10 확정 순서**:
```
Cover → TOC → Glossary → Key Charts → Main Idea
→ 기업개요 → 산업분석 → 기업분석
→ Key Debates → Variant Perception
→ 투자포인트①②③
→ 재무분석 → Peer 비교
→ 실적추정 → 밸류에이션
→ 리스크
→ Appendix → Compliance
```

**핵심**: 기업/산업 이해 → 논쟁 구조 → 투자포인트 → 재무/추정/밸류 → 리스크.

### 31-11. sidebar 커버리지 최소 60% (v10, CRITICAL)

**문제**: KSS해운 v10에서 sidebar-layout이 전체 콘텐츠의 12%만 커버. SMIC은 90%+.

**규칙**: 각 섹션의 **모든 소제목(h3) + 본문(p) + 테이블 + 차트**가 sidebar_wrap 안에 있어야 한다.

```python
# ✅ 올바른 패턴: 섹션 전체를 여러 sidebar_wrap으로 감쌈
h += sidebar_wrap(kws1, block1)  # 소제목1 + 본문 + 차트
h += sidebar_wrap(kws2, block2)  # 소제목2 + 본문 + 차트
h += sidebar_wrap(kws3, block3)  # 소제목3 + 본문 + 테이블

# ❌ 금지: 첫 sidebar_wrap만 쓰고 나머지 전폭
h += sidebar_wrap(kws, intro_only)
h += rest_of_content  # ← 이게 전폭으로 나옴
```

**CSS로 content-area 안 차트 허용**:
```css
.content-area .chart-box { max-width:100%; margin:12px 0; }
.content-area .chart-pair { max-width:100%; }
.content-area img { max-width:100%; }
```

### 31-12. 도표 중복 방지 규칙 (v10)

**문제**: 매출+OPM 차트가 5회, PER 비교 3회, 부채비율 3회 등 동일 데이터가 다른 섹션에서 반복.

**규칙**:
- 같은 데이터를 차트로 **최대 2회** (본문 1회 + Key Charts or Appendix 1회)
- 3회 이상 나오면 Evaluator 경고
- 본문에서 다룬 차트를 Appendix에서 테이블로 보여주는 건 OK (형식이 다르므로)
- **핵심 숫자(COA 잔액 등) 텍스트 반복은 최대 3회** — 초과 시 data_tip으로 대체
