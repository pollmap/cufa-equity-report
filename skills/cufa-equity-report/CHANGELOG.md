# CUFA Equity Report Skill — CHANGELOG

## v16.1 — 2026-04-12 (버그 수정 + PWA + 공유 헬퍼)

### 버그 수정

- `sections/section3_business_setup.py`: `_render_industry_checklist()` 함수 미구현으로 인한 `NameError` 수정 — 함수 본체 추가
- `evaluator/run.py::_count_catalysts()`: 재무 테이블 연도("2025년 매출" 등)가 Catalyst로 오탐되는 버그 수정
  - 기존: 날짜 패턴 전체 카운팅
  - 수정: catalyst 전용 섹션 내 `<li>`/`<tr>` 항목 우선 카운팅 → 없으면 "날짜 + 설명" 패턴만

### 신규 기능

| 파일 | 내용 |
|---|---|
| `builder/pwa.py` | PWA 지원 — `gen_manifest()` / `gen_service_worker()` / `gen_pwa_meta_tags()` |
| `post_processing/share.py` | 공유 헬퍼 — `serve_local()` / `copy_path()` / `zip_report()` |

### 수정

- `builder/core.py`: `_gen_head()`에 PWA 메타 태그 주입, `write_output()`에서 manifest.json + sw.js 동시 저장
- `builder/__init__.py`: pwa 3개 함수 re-export 추가

### 커밋

`27ef25d` — feat: v16.1

---

## v16.0 — 2026-04-12 (HF 퀀트 실행가능성 전환 완료)

### Breaking Changes

- **Evaluator v2 폐기** → v3 (실행가능성 binary 12개)
  - 분량 기반 (80K자/25SVG/25TBL) 완전 제거
  - SMIC 문체 강제 (동사/본서/전술한) 완전 폐기
- **11섹션 → 7섹션 HF 구조** (BLUF/Thesis/Business/Numbers/Risks/Trade/Appendix)
- `sections/minima.py` 삭제 (섹션별 최소 자수 폐기)
- `post_processing/smic_injector.py` 삭제
- `sections/section1_company.py` ~ `section11_appendix.py` 11개 삭제

### 신규 파일 (13개)

| 파일 | 역할 |
|---|---|
| `trade_ticket/__init__.py` | Trade Ticket 패키지 |
| `trade_ticket/schema.py` | TradeTicket 스키마 + validate() |
| `trade_ticket/generator.py` | config → TradeTicket |
| `trade_ticket/backtest_hook.py` | QuantPipeline 연동 |
| `trade_ticket/feedback.py` | Phase 7 복기 엔진 |
| `sections/section1_bluf.py` | Investment Summary (BLUF) |
| `sections/section2_thesis.py` | 3축 Thesis |
| `sections/section3_business_setup.py` | Business & Industry |
| `sections/section4_numbers.py` | Financial + Peer + Valuation 통합 |
| `sections/section5_risks.py` | Bear Case First + Kill Conditions |
| `sections/section6_trade.py` | Trade Implementation ⭐ |
| `sections/section7_appendix.py` | 압축 Appendix A-1~A-4 |
| `SKILL_legacy_v15_backup.md` | v15 원본 백업 |

### 수정 파일

| 파일 | 변경 내용 |
|---|---|
| `SKILL.md` | 1,306줄 v15 → ~680줄 v16 (7섹션 + Trade Ticket + Evaluator v3) |
| `evaluator/criteria.py` | HARD_MIN/SMIC → 12개 실행가능성 binary EvaluatorV3Criteria |
| `evaluator/run.py` | 분량 카운팅 → actionability regex + 하드코딩 ticker 제거 (버그 수정) |
| `sections/__init__.py` | 11섹션 → 7섹션 매핑 |
| `config/_template.py` | StockConfig에 trade_ticket/kill_conditions/backtest_config/feedback_loop 추가 |
| `builder/core.py` | docstring v16 업데이트 (smic_inject 참조 제거) |
| `builder/css.py` | .ticket-box / .thesis-box 클래스 추가 |
| `preflight/industry_checklist.py` | 조선 산업 체크리스트 추가 (11개 항목) |
| `skill.meta.json` | version 16.0, description 업데이트 |
| `README.md` | v16 전면 재작성 |

### 버그 수정

- `evaluator/run.py::_has_trade_ticket()`: HD현대중공업 티커(329180) 하드코딩 제거 → 범용 패턴으로 교체

### 검증

- HD현대중공업 HF 프로토타입: Evaluator v3 12/12 ALL PASS 확인
- Trade Ticket YAML 파싱 검증 완료

---

## v15.2 — 2026-04-11 (확장 포인트 전체 구현 완료)

### 신규 모듈
- `sections/` — 14 파일 (base + minima + __init__ + 11 섹션 빌더)
  - `minima.py` — `SectionMinimum` + `SECTION_MINIMA` (11섹션 총 82,000자 분배)
  - `base.py` — `SectionData` dataclass + `assemble_section()` 공통 파이프라인
  - `section1_company.py` ~ `section11_appendix.py` — 11개 opinion-laden 스캐폴더
  - `SECTION_BUILDERS` dict — 동적 호출 매핑 (1~11)
- `builder/phase65_backtest.py` — Nexus `backtest_run` 래퍼
  - `StrategySpec`, `BacktestResult`, `DEFAULT_STRATEGIES` (MA_cross/Momentum/Mean_reversion)
  - `run_phase65()` → `list[BacktestResult]`, `save_raw()` JSON 보존
- `post_processing/rerating_note.py` — Re-rating v2 블록 생성기
  - `RatingChange`, `ReratingNoteV2` dataclass
  - `gen_rerating_note_v2()` — 커버 직후 삽입용 HTML (id="rerating_v2" 자동 보호)
- `README.md` — 전체 스킬 문서 (Quick Start + 아키텍처 + 상수 + Fail Code + 사용 예시)

### 스모크 테스트 (ALL PASS)
- sections/ 11개 빌더 개별 렌더 확인
- SECTION_BUILDERS[1..11] 동적 호출 확인
- 11섹션 통합 빌드 17,491자 HTML 생성 확인
- phase65_backtest, rerating_note 데이터클래스 + 함수 동작 확인
- total_min_chars = 82,000 / total_min_charts = 29 / total_min_tables = 30 확인

### 설계 원칙
- **sections/ 는 구조 스캐폴더**: 콘텐츠 아닌 형태 정의. 데이터는 `SectionData` 로 주입
- **IP 섹션 3/4/5/10 은 counter_args 강제**: 없으면 `ValueError`
- **Section 1 은 `chart_cols=1`**: 기업개요 도넛은 단독 배치 (다른 섹션은 2열 페어)
- **Re-rating 블록은 id="rerating_v2"**: `protect_replace` 의 보호 영역으로 자동 등록

---

## v15.1 — 2026-04-11 (builder/ 모듈 포팅 완료)

### Builder 모듈 신설 (build_template.py → builder/ 8개 모듈)
- `builder/core.py` — `build_report()`, `BuildContext`, `write_output()`
- `builder/css.py` — `gen_css()` 단일 표준 CSS (HD건설기계 v4-1)
- `builder/design_tokens.py` — `CSS_VARS`, `CHART_COLOR_ROLES`, `BORDER_RADIUS`, `FONT_FAMILY`
- `builder/figure.py` — `FigureCounter` 클래스 + 전역 `fig_num()`, `reset_figures()`
- `builder/svg.py` — 32종 SVG 차트 헬퍼 (svg_radar **삭제**, v13 금지)
- `builder/helpers.py` — `section_header`, `sidebar_wrap`, `table`, `backtest_result_table`
- `builder/components.py` — `counter_arg`, `expand_card`, `chart_with_context`, `add_source`, `data_tip`, `scenario_tabs`, `proprietary_metric`, `valuation_rationale`, `implied_per_check`
- `builder/markdown.py` — `md_to_html()`, `read_md()` 스탠드얼론 Markdown 변환기

### 아키텍처 개선
- **svg_radar 완전 제거** — v13 금지 규칙 준수
- **모듈 전역 상태 제거** — 기존 `_fig_counter` 모듈 딕셔너리 → `FigureCounter` 클래스
- **종목별 하드코딩 제거** — `section_header()` 는 `company_name`/`ticker` 를 매개변수로 받음 (기존: 모듈 전역 `COMPANY_NAME`)
- **type annotations 추가** — 모든 공개 함수 시그니처
- **`builder/__init__.py`** — 50+ 심볼 re-export

### 스모크 테스트 (ALL PASS)
- 10개 테스트: svg_bar, svg_donut, section_header, sidebar_wrap, table, counter_arg, add_source, md_to_html, gen_css, build_report empty
- 전체 empty build: 11,957 chars HTML 생성 확인

---

## v15.0 — 2026-04-11 (표준화 전면 재설계)

### Breaking Changes
- **SKILL.md 전면 재작성**: 5,268줄 → 1,306줄 (75% 감축)
- 종목별 하드코딩 수치를 모두 `config/{stock_code}.py`로 이동
- 임계값을 frozen dataclass 상수로 추출 (`PreflightThresholds`, `EvaluatorCriteria`)
- 검증 케이스는 Appendix A 부록으로 분리 (`CASE-{stock_code}-v{N}` 형식)
- 과거 버전 히스토리는 본 CHANGELOG로 분리

### New Modules (실행 가능 Python)
- `preflight/` — Phase 0 검증
  - `thresholds.py` — `PreflightThresholds`, `PREFLIGHT`
  - `checker.py` — `preflight_validate()`, `PreflightConfig`, `PreflightResult`
  - `mcp_client.py` — `NexusMCPClient` (Streamable HTTP + SSE)
  - `tool_schemas.py` — `TOOL_SCHEMAS`, `validate_args()`
  - `dart_parser.py` — `split_cfs_ofs()`, `get_account_value()`
  - `industry_checklist.py` — `INDUSTRY_CHECKLIST`
- `evaluator/` — v2 자동 검증
  - `criteria.py` — `EvaluatorCriteria`, `EVAL`
  - `run.py` — `evaluate()`, `EvaluationResult`
- `post_processing/` — 빌드 후 처리
  - `protect_replace.py` — `protected_replace()`, 보호-치환-복원
  - `smic_injector.py` — `smic_inject()`, '동사' 주입
- `config/_template.py` — 종목 config 템플릿

### Fail Code 체계 표준화
- `F1_FINANCIAL_DRIFT` — 재무 드리프트 초과
- `F1_SIGN_FLIP` — 영업손익 부호 반전
- `F2_PRICE_DRIFT` — 주가 드리프트 초과
- `F2_VOLATILITY` — 1년 수익률 ±30% 초과 (Re-rating Mode)
- `F3_TRIPLE_CHECK` — PBR × BPS ≠ Price
- `F4_RAW_MISSING` — 원본 응답 미보존
- `F5_INDUSTRY` — 산업 체크리스트 누락

### 문서 정리
- 현대건설(000720) v2 Re-rating 사례를 부록에 기록 (`CASE-000720-v2`)
- 과거 버전 상세 이력은 `SKILL_legacy_v14_2_backup.md` 참조
- 금지 규칙(NEVER-DO) Appendix C로 통합

---

## v14.2 — 2026-04-11 (v15 마이그레이션 준비)

- Pre-flight Checklist 초안 추가 (현대건설 사례 반영)
- 보호-치환-복원 패턴 명문화 (섹션 29-3b)
- Nexus MCP 도구 스키마 힌트 문서화

**참고**: v14.2는 v15.0에 흡수되었으며, 독립 릴리즈로 사용되지 않음.

---

## v14.1 — 2026-04-04 (Evaluator v2 ALL PASS 시스템)

- HARD_MIN + SMIC_STYLE + HALLUCINATION 3단 검증 루프 확정
- HD건설기계 v4-1 CSS 표준화
- SVG 15종 인라인 (matplotlib 의존 제거)
- `template/` + `builder/` 분리 구조
- 이노스페이스 사례 ALL PASS 검증

---

## v13.2 — 2026-04-03 (Jeff Sun + KIS Backtest)

- Jeff Sun 기술적 분석 지표 5종 (ADR% / RVoL / ATR% / VARS / VCP)
- 3-Stop 리스크 관리 전략
- 포지션 사이징 (ADR% 기반)
- KIS Backtest MCP 연동 프로토콜
- Phase 6.5 백테스트 검증 단계 추가

---

## v13.1 — 2026-04-03 (도구 체인 확장)

- Draw.io MCP 연동
- QuantAgent 기술적 분석 패턴
- 정량 분석 도구 체인 (scipy/sklearn/statsmodels)

---

## v13.0 — 2026-04-03 (15편 역설계)

- 15편 벤치마크 보고서 역설계 완료 (SMIC 5 + YIG 7 + STAR 2 + 리튼 1)
- svg_radar 완전 금지 (grouped_bar/scatter로 대체)
- 산출물 3종 확정: HTML + Excel + Markdown
- DOCX 제거
- 추론 4~5단계 체인 표준화
- 2중 반박 구조 (인라인 + counter_arg 블록)

---

## v12.0 — 2026-03-30 (SMIC 문체 정립)

- "동사(同社)는" 지칭 원칙 (80회+/편)
- "본서는/에서는" 주장 패턴
- "전술한/후술할" 크로스레퍼런스
- 볼드-첫문장 원칙 (150개+)
- 전환어 레지스트리 7종

---

## v11.0 — 2026-03-28 (워크플로우 재설계)

- 엑셀을 Single Source of Truth로 확정
- Phase 0~6 파이프라인 정식화
- 서브에이전트 6개 병렬 빌드 패턴

---

## v10.0 — 2026-03-27 (KSS해운 실전 교훈)

- 섹션 29 "v10 패치노트" 신설
- 서브에이전트 병렬 빌드 패턴
- SVG 차트 품질 규칙 (auto_base, 텍스트 겹침 방지)
- `add_source` 중복 방지
- 이미지 사용 규칙 (기업 홈페이지 URL 허용)
- Float TOC 본문 겹침 방지
- 사이드바 커버리지 60% 규칙

---

## v9.0 — 2026-03-25 (벤치마크 14건 종합)

- YIG/SMIC/STAR/EIA 14건 종합 벤치마크
- Key Debates / Variant Perception 신설
- Re-rating 트리거 초안
- 방법론 8종 매트릭스 확정

---

## v8.0 — 2026-03-20 (89점 자동 달성)

- Markdown-first 워크플로우
- counter_arg 3건+ 강제
- ASP 분해 테이블 표준

---

## v7.0 — 2026-03-18 (스크롤 UX)

- 진행률 바 / Float TOC / Section Dots / Back to Top / Page Break 5종
- requestAnimationFrame 최적화

---

## 이전 버전

상세 이력은 `SKILL_legacy_v14_2_backup.md`의 관련 섹션 참조.
