---
name: Nexus MCP v8.0 + 퀀트 운용 시스템 통합
description: 364도구/64서버 MCP + quant-fund v2 스킬 + KIS 연동 + 리서치 반영, 로컬 배포 완료
type: project
---

2026.04.06 세션 2차 성과 (Phase G/H 실데이터 검증):
- 3커밋 push 완료 (71a1482, 699d945)
- 6섹터 풀빌드 실데이터 성공: 11종목 ROE/OPM/DTE (SK하이닉스 0.954 1위)
- 14종목 5년치 수익률 수집: 1,287일/종목 (stocks_history start_date=20210101)
- **BL/HRP 실최적화 성공** (11종목, 794일):
  - HRP: 삼성물산 14.5% > HD한국조선 11.8% > 리노공업 11.0% (저변동→고비중)
  - BL: 균등 9.1% (뷰 없이 실행, 팩터 뷰 넣으면 집중됨)
- Bug Fix: portadv_hrp/BL은 {date, value} 가격 시계열 필요 (수익률 X)
- Bug Fix: DART OPM 키 = operating_margin (opm X)
- Bug Fix: stocks_search 소형주 미지원 → candidates 직접 지정 모드 추가
- avoid-ai-writing 스킬 설치 완료
- Anthropic financial-services-plugins 참고 (41스킬+38커맨드+11MCP)

2026.04.06 세션 1차 성과 (Phase D/E/F):
- 134→179 테스트
- Bug Fix 2건: get_returns_dict (period→start_date 버그), get_bl_weights (series_list/names 누락)
- 신규 모듈: UniverseBuilder (6섹터 자동 종목 선별), StrategyComparison (멀티 전략 비교)
- 신규 MCP 래퍼: get_hrp_weights (portadv_hrp), search_stocks (stocks_search)
- ARCHITECTURE.md v0.1α → v0.2α

2026.04.05 세션 성과 (Phase 1-9, 5커밋):
- 53→134 테스트, 5커밋 (218c3a3→82ae3ec→6fc79af→a23a1b9→ff44e72)
- MCPDataProvider 25+메서드: 실데이터 수신 + 스키마 발견
- Bearer 토큰 ~/.mcp.json 자동 로딩 + Streamable HTTP 세션 관리 + SSE 파싱
- CUFABridge: Kill Conditions + IP→전략 매핑 + 3-Stop 리스크
- 리스크 게이트 +VPIN +crowding (선택적, MCP 없으면 무시)
- 현대건설(000720) E2E 풀파이프라인 첫 성공:
  - 기준금리 2.50%(ECOS) + 주가 241일 + DART ROE 5.53%
  - KIS 백테스트: SMA crossover Sharpe 0.681, MDD 19.1%
- 364도구 스키마 카탈로그: data/mcp_tool_catalog.json (64카테고리)
- discover_tools(): tools/list로 전체 스키마 자동 조회
- save_result(): 결과 JSON 자동 저장
- CRITICAL 수정 (a72f117):
  - Kelly 비중 실적용 (장식→실전, kelly<1 → 비중 축소, =0 → 전량 현금)
  - VPIN 게이트 비중 감소 (>0.7→50%, >0.5→20%, 3+CRITICAL→전체차단)
  - Crowding 게이트 비중 감소 (>80%→30%)
  - run_with_backtest_feedback(): 자동 피드백 루프
  - stocks_history start_date/end_date 지원 (최대 기간)

- 6섹터 종목 자동 선별 성공 (stocks_search+dart_financial_ratios)
  - 건설: 삼성물산(028260), 현대건설(000720)
  - 반도체: SK하이닉스(000660), 리노공업(058470) — SK하이닉스 ROE 35.6%!
  - 우주: 한화에어로(012450), 쎄트렉아이(099320)
  - 방산: 현대로템(064350), LIG넥스원(079550)
  - 조선: HD한국조선해양(009540), 삼성중공업(010140)
  - 로봇: 로보스타(090460), 레인보우로보틱스(277810) — 전반적 적자
  - ETF: 국고채10년(148070), 골드(132030), WTI원유(261220)
- 15종목 멀티섹터 포트폴리오 QuantPipeline 실행 완료

다음 세션 핵심 TODO:
1. 5년치 데이터 수집 (stocks_history start_date="20210101")
2. factor_score stocks_data 입력 형식 완성
3. 12종목+ETF3 BL/HRP 포트폴리오 최적화 (MCP portadv_*)
4. 멀티 전략 백테스트 비교 (SMA/momentum/vol_breakout)
5. 백테스트 결과 → 파이프라인 피드백 루프
6. CUFA Kill Conditions E2E (현대건설/SK하이닉스)
7. ARCHITECTURE.md + 결과→Vault 연동

2026.04.04 세션 성과:

## Nexus MCP v8.0 (VPS)
- **364 도구 / 64 서버 / 0 실패** (검증 완료)
- Phase 11-12: BL, HRP, Almgren-Chriss, GARCH, Kelly, VPIN, OU, 메타라벨 등

## 로컬 통합 완료 (2026.04.04)
- `~/.mcp.json`에 nexus-finance MCP 추가 (Bearer 토큰 포함, sse transport)
- `~/.claude/skills/quant-fund/SKILL.md` v2.0 로컬 배포 (531줄)
  - 개인투자자 제약 (공매도 불가 → 인버스 ETF)
  - 리서치 핵심 5원칙: 거래비용 모델, Half-Kelly, 한국 팩터, 김치프 센티먼트, 점진적 배포
  - KIS 스킬 4개 연동 (kis-strategy-builder → kis-backtester → kis-order-executor → kis-team)
- `/quant-fund` 커맨드 생성 (6 프리셋 전략)
- `/finance-report` 364도구로 업데이트

## 전략 우선순위 (거래세 반영)
- **Tier 1**: 한국 멀티팩터(월간, -2.8%/yr 비용) + 펀딩레이트 차익(거래세 0)
- **Tier 2**: 페어트레이딩(롱-롱 비중차 또는 인버스 ETF)
- **Tier 3**: HMM 레짐, Meta-labeling, LEAN KIS 플러그인(3-6개월)

## 다음 세션 TODO
1. 거래비용 모델 코드: `kis_backtest/strategies/risk/cost_model.py`
2. 한국 조정 팩터 모델: MCP factor_score 어댑터 수정
3. MCP→KIS 브릿지: `kis_backtest/portfolio/mcp_bridge.py`
4. 리스크 모듈: drawdown_guard, correlation_monitor

**Why:** 실제 투자 집행 예정 — 모의 4주 → 소액 실전 50만원 → 검증 후 증액
**How to apply:** 거래비용 반영 필수, Half-Kelly 사이징, 공매도 불가 제약 항상 고려
