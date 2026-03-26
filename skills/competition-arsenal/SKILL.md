---
name: competition-arsenal
description: "한국 금융권 공모전/경시대회 통합 무기고. 데이터 수집→API/웹 검증→시각화(PNG/HTML)→보고서(DOCX)→발표(PPTX)→데이터부록(XLSX) 풀파이프라인. 대회 프리셋 6종(debate/research/idea/data/paper/public-data). nexus-finance MCP 126도구+공공데이터+arxiv 연동. 목업 데이터 절대 금지. 트리거: '공모전', '경시대회', '토론 자료', '시각자료', '발표 자료', '차트 만들어', '대회 준비', '데이터 검증', 'competition', '경진대회', '공모전 차트', '발표용 그래프', '보고서 차트', '대회용'."
---

# competition-arsenal: 공모전/경시대회 통합 무기고

## 1. 핵심 철학

- **목업 데이터 절대 금지**: 모든 수치는 검증된 출처 기반. "문서에 있으니까 맞겠지"는 금지
- **검증 먼저, 차트 나중**: 데이터 정확성 확인 후 시각화
- **출처가 없으면 차트도 없다**: 기관명 + 보고서명 + 발행일 구체적 표기
- **1차트 1메시지**: 차트 하나에 전달할 핵심은 하나
- **대회 프리셋 선택 → 자동 파이프라인**: 대회 유형에 맞는 산출물 자동 조합
- **병렬 실행**: 데이터 검증, 차트 생성, 보고서 빌드를 최대한 병렬로
- **한국어 우선**: 폰트, 금액 표기, 기관명, 용어 정의 모두 한국어 기준

## 2. 마스터 워크플로우 (7단계)

```
[1] 대회 프리셋 선택
  → [2] 데이터 수집
    → [3] API/웹 검증 (병렬)
      → [4] 검증 테이블 작성
        → [5] 시각화 생성 (프리셋별)
          → [6] 산출물 빌드 (프리셋별)
            → [7] 품질 검증 + 체크리스트
```

## 3. 대회 프리셋 6종

### 3.1 `debate` — 토론대회 / 경시대회

**적용 대회**: 한국은행 통화정책 경시대회, 전세 토론, 정책 토론

**산출물**: PNG 차트 + 발표 대본 + 발표 순서표

**워크플로우**:
1. 논점/데이터 정리 → 검증 테이블
2. matplotlib 차트 7~10장 (다크 테마, 300dpi)
3. 차트별 1줄 메시지 + 발표 순서 + 시간 배분
4. 예상 반박 + 즉답 테이블
5. 3단계 화법 (공감→전환→결론) 대본

**차트 스타일**: 다크 테마 (bg=#1a1a2e), 큰 글씨, 색상 의미 일관성
**발표 순서 원칙**: Hook → Trend → Compare → Impact → Counter → Evidence → Close

---

### 3.2 `research` — 리서치 보고서

**적용 대회**: 리서치 아카데미아, CFA Research Challenge, DB보험금융공모전(IFC)

**산출물**: DOCX 보고서 (40,000자+) + PNG 차트 + XLSX 데이터 부록

**워크플로우**:
1. 산업/기업 리서치 (nexus-finance MCP + WebSearch + arxiv)
2. 재무데이터 수집 (DART + ECOS + KOSIS)
3. 마크다운 파트별 작성 (5파트, 각 8,000자+)
4. matplotlib 차트 15장+ (보고서 삽입용)
5. python-docx 또는 docx-js로 보고서 빌드
6. XLSX 데이터 부록 (IS/BS/CF/Valuation)

**연계 스킬**: `bok-report-writing` (보고서 형식), `cufa-equity-report` (기업분석)

**품질 기준**:
| 항목 | 최소 | 목표 |
|------|------|------|
| 글자 수 | 30,000자 | 40,000자+ |
| 참고문헌 | 20개 | 30개+ |
| 차트 | 10장 | 15장+ |
| 테이블 | 8개 | 15개+ |
| 그래프 "읽는 법" | 모든 차트 | 모든 차트 |

**주의**: CFA Research Challenge는 100% 영어. KIC 논문 공모전은 **AI 사용 논문 심사 제외** 규정 있음.

---

### 3.3 `idea` — 아이디어/비즈니스 공모전

**적용 대회**: 한화생명 미래금융인재, 핀테크 아이디어 공모전, 신한 AI IDEATHON

**산출물**: PPTX 슬라이드 (15~25장) + 인터랙티브 HTML (선택)

**워크플로우**:
1. 시장 조사 + 트렌드 분석 (WebSearch + GDELT)
2. 비즈니스 모델 캔버스 설계
3. TAM/SAM/SOM 시장 규모 산출
4. 프로토타입/목업 (필요시 frontend-design 스킬)
5. PPTX 빌드 (python-pptx)
6. 인터랙티브 데모 HTML (mla-dsa-analysis 스킬)

**연계 스킬**: `pptx` (슬라이드), `mla-dsa-analysis` (인터랙티브 HTML), `frontend-design` (프로토타입)

**슬라이드 구조** (15장 기준):
```
1. 표지
2. 문제 정의 (Pain Point)
3. 시장 규모 (TAM/SAM/SOM)
4. 솔루션 개요
5-7. 핵심 기능 (3장)
8. 기술 아키텍처
9. 비즈니스 모델
10. 경쟁 분석
11. 차별화 포인트
12. 로드맵
13. 팀 소개
14. 재무 계획
15. Q&A
```

---

### 3.4 `data` — 데이터분석/AI 경진대회

**적용 대회**: KRX 데이터 경진대회, 빅콘테스트, 토스 NEXT ML, WorldQuant IQC, 금융보안원 AI Challenge

**산출물**: 분석 코드 + HTML 리포트 + XLSX 결과 + 모델 파일

**워크플로우**:
1. 데이터 탐색 (EDA) — pandas + matplotlib
2. 피처 엔지니어링
3. 모델 학습 + 평가
4. 결과 시각화 (인터랙티브 HTML)
5. 제출용 코드 정리

**연계 스킬**: `research-report-interactive` (분석 리포트), `xlsx` (결과 데이터)

**시각화 도구 우선순위**:
1. nexus-finance MCP viz_* (빠른 생성)
2. matplotlib (커스텀 차트)
3. mla-dsa-analysis (인터랙티브)

---

### 3.5 `paper` — 학술 논문

**적용 대회**: KIC 논문, 한경 경제논문, 예금보험공사 논문, 한국은행 논문

**산출물**: DOCX 논문 (학술 형식) + PDF

**워크플로우**:
1. 문헌 조사 (arxiv MCP + WebSearch + ECOS)
2. 연구 방법론 설계
3. 데이터 분석 + 결과
4. 마크다운 작성 (학술 구조: 서론→문헌→방법→결과→결론)
5. DOCX 빌드 (학술 형식: 각주, 참고문헌 APA)

**연계 스킬**: `bok-report-writing` (보고서 형식), `docx` (문서 빌드)

**주의사항**:
- KIC 논문 공모전: **AI 도구 사용 논문 심사 제외** → 코드 자동생성 결과물 직접 제출 금지
- 예금보험공사: 수상 시 **채용 서류전형 면제** (5년 유효)

---

### 3.6 `public-data` — 공공데이터 활용 공모전

**적용 대회**: 고용노동 공공데이터 공모전, 서울시 빅데이터, 교육 공공데이터 AI 활용대회

**산출물**: 인터랙티브 HTML + PPTX + 소스 코드 + 데이터 파이프라인

**워크플로우**:
1. 공공데이터포털(data.go.kr) API 탐색
2. 데이터 수집 파이프라인 구축
3. 분석 + 시각화 (인터랙티브 HTML 필수)
4. 서비스/제품 프로토타입
5. 발표 자료 (PPTX)

**연계 스킬**: `frontend-design` (프로토타입), `mla-dsa-analysis` (대시보드)

**가점 요소**:
- 예비창업자 가점 1점
- 주관기관 데이터 활용 시 가점 2점
- 서로 다른 분야 데이터 결합 시 가점

---

## 4. 데이터 파이프라인

### 4.1 nexus-finance MCP 126도구 카테고리

**거시경제 (한국은행 ECOS)**
| 도구 | 데이터 |
|------|--------|
| `ecos_get_base_rate` | 기준금리 |
| `ecos_get_gdp` | GDP |
| `ecos_get_exchange_rate` | 환율 |
| `ecos_get_m2` | M2 통화량 |
| `ecos_get_macro_snapshot` | 거시 스냅샷 |
| `ecos_get_stat_data` | ECOS 범용 조회 |
| `ecos_search_stat_list` | ECOS 통계 검색 |

**부동산 (한국부동산원 R-ONE + 국토부)**
| 도구 | 데이터 |
|------|--------|
| `rone_get_pir` | PIR (소득대비주택가격) |
| `rone_get_jeonse_index` | 전세가격지수 |
| `rone_get_apt_price_index` | 아파트 매매가격지수 |
| `rone_get_market_summary` | 부동산 시장 요약 |
| `rone_get_price_comparison` | 가격 비교 |
| `rone_list_regions` | 지역 목록 |
| `realestate_apt_trades` | 아파트 실거래가 |
| `realestate_sigungu_codes` | 시군구 코드 |

**통계청 (KOSIS)**
| 도구 | 데이터 |
|------|--------|
| `kosis_get_table` | 통계표 직접 조회 |
| `kosis_search_tables` | 통계표 검색 |
| `kosis_get_housing_price` | 주택가격지수 |
| `kosis_get_population` | 인구 |
| `kosis_get_unemployment` | 실업률 |

**기업/금융 (DART + 주식)**
| 도구 | 데이터 |
|------|--------|
| `dart_company_info` | 기업 기본정보 |
| `dart_financial_statements` | CFS 재무제표 |
| `dart_financial_ratios` | 재무비율 |
| `dart_major_shareholders` | 대주주 |
| `dart_search_company` | 기업 검색 |
| `fsc_stock_price` | 주가 (금융위) |
| `fsc_bond_price` | 채권가격 |
| `stocks_quote` | 실시간 시세 |
| `stocks_history` | 주가 시계열 |
| `stocks_search` | 종목 검색 |
| `stocks_beta` | 베타 |
| `stocks_market_overview` | 시장 개요 |

**미국/글로벌**
| 도구 | 데이터 |
|------|--------|
| `us_stock_quote` | 미국 주가 |
| `us_company_profile` | 미국 기업 프로필 |
| `us_economic_calendar` | 미국 경제 캘린더 |
| `us_market_news` | 미국 시장 뉴스 |
| `macro_imf` | IMF 데이터 |
| `macro_oecd` | OECD 데이터 |
| `macro_worldbank` | 세계은행 |
| `macro_bis` | BIS 데이터 |
| `macro_datasets` | 거시 데이터셋 |

**에너지/원자재/해운**
| 도구 | 데이터 |
|------|--------|
| `energy_crude_oil` | 원유 |
| `energy_natural_gas` | 천연가스 |
| `energy_price_snapshot` | 에너지 스냅샷 |
| `maritime_bdi` | BDI 지수 |
| `maritime_container_index` | 컨테이너 지수 |
| `maritime_freight_snapshot` | 해운 스냅샷 |

**뉴스/여론**
| 도구 | 데이터 |
|------|--------|
| `news_search` | 뉴스 검색 |
| `news_keyword_volume` | 키워드 볼륨 |
| `news_market_sentiment` | 시장 심리 |
| `news_trend` | 뉴스 트렌드 |
| `gdelt_search` | GDELT 글로벌 뉴스 |
| `gdelt_korea_news` | GDELT 한국 뉴스 |
| `gdelt_timeline` | 뉴스 타임라인 |

**학술/특허/정치**
| 도구 | 데이터 |
|------|--------|
| `academic_arxiv` | arXiv 논문 |
| `academic_semantic_scholar` | Semantic Scholar |
| `academic_openalex` | OpenAlex |
| `academic_multi_search` | 멀티 학술 검색 |
| `patent_search` | 특허 검색 |
| `patent_trending` | 트렌딩 특허 |
| `politics_bills` | 법안 |
| `politics_finance_bills` | 금융 법안 |
| `politics_recent_bills` | 최근 법안 |

**밸류에이션**
| 도구 | 데이터 |
|------|--------|
| `val_dcf_valuation` | DCF 밸류에이션 |
| `val_calculate_wacc` | WACC |
| `val_peer_comparison` | Peer 비교 |
| `val_sensitivity_analysis` | 민감도 분석 |
| `val_cross_market_comparison` | 크로스마켓 |
| `val_normalize_gaap` | GAAP 정규화 |

**시각화 (nexus-finance viz)**
| 도구 | 차트 유형 |
|------|----------|
| `viz_bar_chart` | 바 차트 |
| `viz_line_chart` | 라인 차트 |
| `viz_pie_chart` | 파이 차트 |
| `viz_scatter` | 산점도 |
| `viz_heatmap` | 히트맵 |
| `viz_dual_axis` | 이중축 |
| `viz_waterfall` | 워터폴 |
| `viz_candlestick` | 캔들스틱 |
| `viz_correlation_matrix` | 상관행렬 |
| `viz_sensitivity_heatmap` | 민감도 히트맵 |

### 4.2 검증 채널 (우선순위)

1. **nexus-finance MCP** (최우선) — 위 도구 직접 호출
2. **WebSearch** — 공식 보도자료, 기사 교차검증
3. **WebFetch** — 특정 URL 직접 접근
4. **arxiv MCP** — 학술 논문 (`mcp__arxiv-mcp-server__search_papers`)
5. **직접 API** — 사용자 제공 키 (MOLIT, ECOS, KOSIS, DART, FRED)

### 4.3 검증 테이블 형식

```markdown
| # | 데이터 항목 | 문서 수치 | 검증 결과 | 판정 | 출처 |
|---|-----------|----------|----------|------|------|
| 1 | ... | ... | ... | 정확/근사/수정필요/확인불가 | [기관명 보고서명](URL) |
```

---

## 5. 시각화 가이드

### 5.1 차트 유형 선택 매트릭스

| 데이터 유형 | 추천 차트 | matplotlib | MCP viz |
|-----------|----------|:----------:|:-------:|
| 국제/도시 순위 비교 | Horizontal Bar | O | O |
| 비중 변화 추이 | Stacked Area | O | - |
| A vs B 비교 | Grouped Bar | O | O |
| 분포/집중도 | Donut / Pie | O | O |
| 시계열 + 전환점 | Bar + Annotation | O | - |
| 스케일 차이 큰 비교 | Log Scale Bar | O | - |
| 핵심 수치 임팩트 | Big Number 인포그래픽 | O | - |
| 누적 변화 분해 | Waterfall | - | O |
| 상관관계 | Heatmap | O | O |
| 2지표 동시 | Dual Axis | O | O |
| 회귀/군집 | Scatter | O | O |
| 주가/시계열 | Candlestick | - | O |
| DCF 민감도 | Sensitivity Heatmap | - | O |
| 프로세스 플로우 | Mermaid / SVG | - | HTML |

### 5.2 matplotlib 공통 스타일

```python
BG = '#1a1a2e'       # 배경
TEXT = '#eaeaea'      # 텍스트
GRID = '#333355'      # 그리드
GREEN = '#4caf50'     # 긍정/찬성/이점
RED = '#ef5350'       # 부정/반대/위험
ORANGE = '#ff9800'    # 주석/전환점/중립
BLUE = '#4fc3f7'      # 기준선/전세/현재
GRAY = '#555555'      # 비교대상/비강조
SUBTEXT = '#aaaaaa'   # 출처 텍스트
BOX_BG = '#222244'    # 인포그래픽 박스

plt.rcParams.update({
    'font.family': 'Malgun Gothic',  # Win: Malgun Gothic / Linux: NanumGothic
    'axes.unicode_minus': False,
})
```

### 5.3 출처 표기 패턴

```python
fig.text(0.5, -0.03,
         '출처: {기관명} 「{보고서명}」 ({발행일})  |  {1줄 메시지}',
         ha='center', fontsize=9.5, color='#aaaaaa', style='italic')
```

### 5.4 한국어 특화 규칙

- **폰트 자동 감지**: Malgun Gothic → NanumGothic → AppleGothic 순
- **금액 표기**: 만원/억원/조원 자동 (예: 23,000,000,000 → 230억원)
- **날짜**: 2024년 12월 / 2024.12
- **기관명**: 공식 약칭 사용 (국토교통부, 한국은행, 금융위원회, 통계청)
- **용어 정의**: 전문용어 첫 등장 시 괄호 설명 (예: PIR(소득대비주택가격비율))

---

## 6. 크로스스킬 오케스트레이션

### 6.1 스킬 연계 맵

```
[competition-arsenal] ← 메인 오케스트레이터
  │
  ├─ [데이터 수집/검증]
  │   ├── nexus-finance MCP (126도구)
  │   ├── arxiv MCP (학술 논문)
  │   ├── WebSearch / WebFetch
  │   └── 사용자 제공 API 키
  │
  ├─ [시각화]
  │   ├── matplotlib → PNG 300dpi
  │   ├── nexus-finance viz_* → MCP 차트
  │   └── mla-dsa-analysis → 인터랙티브 HTML
  │
  ├─ [보고서 빌드]
  │   ├── bok-report-writing → 한국어 보고서 (40,000자+, 보라 테마)
  │   ├── cufa-equity-report → 기업분석 보고서 (DOCX + HTML)
  │   ├── research-report-interactive → DOCX + 인터랙티브 HTML 동시
  │   └── docx → Word 문서 범용
  │
  ├─ [발표 자료]
  │   ├── pptx → PowerPoint 슬라이드
  │   ├── mla-dsa-analysis → 인터랙티브 발표
  │   └── canvas-design → 포스터/인포그래픽
  │
  ├─ [데이터 부록]
  │   └── xlsx → Excel 데이터시트
  │
  └─ [품질 관리]
      ├── gsd-workflow → 대규모 작업 분해/병렬 실행
      └── luxon-problem-solving → audit→fix 패턴
```

### 6.2 프리셋별 스킬 호출 순서

| 프리셋 | 1단계 | 2단계 | 3단계 | 4단계 |
|--------|-------|-------|-------|-------|
| debate | competition-arsenal | (자체 matplotlib) | - | - |
| research | competition-arsenal | bok-report-writing | xlsx | - |
| idea | competition-arsenal | pptx | mla-dsa-analysis | frontend-design |
| data | competition-arsenal | research-report-interactive | xlsx | - |
| paper | competition-arsenal | bok-report-writing | pdf | - |
| public-data | competition-arsenal | frontend-design | pptx | mla-dsa-analysis |

---

## 7. AutoResearch 패턴 (카파시 영감)

### 7.1 병렬 에이전트 오케스트레이션

데이터 검증 시 **최소 3개, 최대 5개** 에이전트 병렬 실행:
```
Agent 1: nexus-finance MCP 거시경제 데이터 검증
Agent 2: nexus-finance MCP 부동산/금융 데이터 검증
Agent 3: WebSearch 보도자료/기사 교차검증
Agent 4: (선택) arxiv 학술 논문 서치
Agent 5: (선택) 국제 비교 데이터 검증
```

### 7.2 반복 개선 루프

```
차트 생성 → 품질 체크 → 문제 발견 → 자동 수정 → 재생성
                ↑                                    │
                └────────────────────────────────────┘
```

**품질 체크 항목**:
- 출처 표기 누락 여부
- 주석 겹침 여부
- Y축 라벨 깨짐 여부
- 색상 의미 일관성
- 한글 폰트 렌더링

### 7.3 program.md 패턴

대회별 "연구 매뉴얼"을 마크다운으로 정의하여 에이전트에 주입:
```
# {대회명} 연구 매뉴얼
## 심사 기준
## 제출 형식
## 데이터 소스
## 시각화 요구사항
## 우수작 패턴
## 주의사항
```

---

## 8. 한국 금융권 대회 레퍼런스

### 8.1 주요 대회 + 산출물 형식

| 대회 | 프리셋 | 산출물 | 채용연계 | 시기 |
|------|--------|--------|---------|------|
| 한국은행 통화정책 경시대회 | debate | 발표 + 자유형식 | - | 연1회 |
| 리서치 아카데미아 | research | 보고서 | 가산점 | 10~11월 |
| DB보험금융공모전(IFC) | research | 보고서+발표 | 글로벌탐방 | 12~2월 |
| CFA Research Challenge | research | 영문보고서+발표 | 글로벌결선 | 8~1월 |
| 한화생명 미래금융인재 | idea | PPT+발표 | 서류면제 | 12~3월 |
| 핀테크 아이디어 공모전 | idea | 기획서+PPT | 사업화지원 | 8~10월 |
| KRX 데이터 경진대회 | data | 분석코드+리포트 | 5년 서류면제 | 10월~ |
| 빅콘테스트 | data | 분석결과+PPT | - | 7~10월 |
| 토스 NEXT ML | data | 코드+모델 | 30팀 서류면제 | 8~9월 |
| KIC 논문 공모전 | paper | 학술논문 | - | 7~9월 |
| 고용노동 공공데이터 | public-data | 서비스+PPT | 장관상 | ~5월 |
| 서울시 빅데이터 | public-data | 분석+PPT | 범정부대회 | 3~5월 |

### 8.2 채용연계 TOP 5

1. **한화생명 미래금융인재** — 1억원 + 서류면제
2. **토스 NEXT ML** — 30팀 서류면제
3. **KRX 데이터 경진대회** — 5년간 서류면제
4. **DB보험금융공모전** — 골드만삭스/KKR 탐방
5. **WorldQuant IQC** — $100,000 + 정규직

---

## 9. 우수작 공통 패턴 10가지 (조사 결과)

공모전 수상작을 분석한 결과 공통적으로 발견되는 시각화/보고서 패턴:

1. **데이터 기반 스토리텔링** — 차트가 논리 흐름에 종속 (차트 먼저가 아님)
2. **핵심 숫자 대형 강조** — TP, WACC, PER 등 킬링 넘버를 40pt+ 볼드
3. **Waterfall/Bridge 차트** — 실적 변동 요인 분해 (매출 증감 원인)
4. **Peer Comparison 테이블** — 동종업체 멀티플 비교 (반드시 포함)
5. **시계열 트렌드 차트** — 주가/실적/매크로 3~5년 추이
6. **Football Field 차트** — Valuation Range 시각화 (DCF/PER/PBR 밴드)
7. **1슬라이드 1메시지** — 컨설팅 스타일, 제목이 곧 결론
8. **색상 2~3가지 일관 유지** — 브랜드 컬러 시스템
9. **모든 차트에 Source 명시** — 출처 없는 차트 = 감점
10. **Executive Summary 1페이지** — 핵심 투자포인트 + 주요 지표 한눈에

## 10. 대회별 제출 형식 상세

| 대회 | 제출물 | 분량 | 심사방식 |
|------|--------|------|---------|
| **한국은행 통화정책** | 예심: Word(규정양식, PDF 실격!), 결선: PPT | 예심 보고서 + PPT무제한 | 서면→발표15분+Q&A 15~20분 |
| **DB보험금융(IFC)** | 논문: Word(바탕체12pt), 기획안: PPT | 무제한(10MB이하) | 실용성40+창의성30+논리성30 |
| **리서치 아카데미아** | 프레젠테이션용 PDF | **40페이지 이내** | 증권사 리서치센터장 5명 직접 심사 |
| **CFA Research Challenge** | Written Report(PDF) + PPT | **본문 10p + Appendix 10~20p** | 글로벌 표준, 필수 7섹션 |
| **금감원 금융공모전** | 문서/PPT/카드뉴스/영상/웹툰 | PPT 20p, 문서 A4 10매 | 세부 비공개 |
| **한화생명 미래금융인재** | PPT→PDF변환 + 5분 영상 | 20MB 이하 | 세부 비공개 |

**핵심 발견**:
- 별도 "시각화 배점"은 없지만, "논리성/전달력/실용성"에서 시각자료 품질이 실질 차별화
- **PPT/PDF가 압도적 주류** (7개 중 6개)
- **최종 심사는 전부 PT 발표** → 시각 커뮤니케이션이 등수 결정
- **CFA RC가 가장 엄격** — 10페이지에 핵심 압축, charts/tables highlight

## 11. Superpowers/GSD/ECC 패턴 적용

### 11.1 Superpowers brainstorming (소크라테스식)
반박 논점(counter_arg) 자동 생성에 활용:
- "이 주장의 가장 약한 고리는?"
- "반대편이 이 데이터를 어떻게 해석할까?"
- "이 결론을 뒤집으려면 어떤 전제가 무너져야 하는가?"

### 11.2 GSD 웨이브 병렬
대규모 보고서를 웨이브로 분해:
```
Wave 1: 산업분석 + 재무분석 + 밸류에이션 (병렬 3개)
Wave 2: 차트 생성 + 테이블 빌드 (병렬 2개)
Wave 3: DOCX 보고서 조립 + PPTX 슬라이드 변환
Wave 4: 품질 검증 + 최종 체크리스트
```

### 11.3 ECC Instincts 패턴
반복 분석에서 발견한 패턴 자동 축적:
- "이 산업은 PER보다 EV/EBITDA가 적합" → 스킬로 승격
- "한국은행 보고서는 항상 이 구조" → 프리셋으로 고정
- "이 차트 유형이 심사위원에게 효과적" → 시각화 가이드에 추가

---

## 12. 안티패턴 (하지 말 것)

1. **검증 없이 차트 만들지 마라** — 목업 = 탈락
2. **출처를 뭉뚱그리지 마라** — "통계청" ❌ → "통계청 「2023 가계동향조사」 Q4 보도자료" ✅
3. **프리셋 없이 시작하지 마라** — 먼저 어떤 대회인지 확인
4. **한 세션에 전부 하려 하지 마라** — Phase 나누기 (CLAUDE.md 규칙)
5. **API 하나 실패했다고 포기하지 마라** — 5중 폴백
6. **AI 사용 금지 대회에 AI 산출물 제출하지 마라** — KIC 논문 주의
7. **영어 대회에 한국어 차트 만들지 마라** — CFA Challenge = 100% 영어
8. **발표 순서 없이 차트만 던지지 마라** — debate 프리셋 필수
9. **보고서 10,000자로 끝내지 마라** — research 프리셋 최소 30,000자

---

## 13. 최종 체크리스트 (프리셋 공통)

- [ ] 대회 프리셋 선택됨
- [ ] 모든 수치에 검증 테이블 작성됨
- [ ] 모든 차트 하단에 구체적 출처 + 발행일
- [ ] 수정 필요 항목 반영 완료
- [ ] 색상 일관성 (초록=긍정, 빨강=부정)
- [ ] 한글 폰트 정상 렌더링
- [ ] 주석 겹침 없음
- [ ] 산출물 형식이 대회 요구사항과 일치
- [ ] 발표 순서/시간 배분 제안 (debate/idea)
- [ ] 글자수/참고문헌/차트수 기준 충족 (research/paper)
- [ ] AI 사용 제한 확인 (paper)
- [ ] 사용자에게 "확인 불가" 항목 고지
