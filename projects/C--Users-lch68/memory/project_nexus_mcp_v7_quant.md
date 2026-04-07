---
name: Luxon AI 퀀트 운용 시스템 v0.1α
description: 7 GitHub 커밋, 53 tests, 상관모니터+팩터→BL자동+포트폴리오vol타겟팅+공매도클리핑 전부 내장
type: project
---

## 최종 상태 (2026.04.05)

### 이번 세션 핵심 개선 (건설적 피드백 반영)
1. **현금 86%→28%**: 종목별→포트폴리오 레벨 vol 타겟팅 (Moskowitz 원래 의도)
2. **공매도 자동 클리핑**: pipeline.run() 내 자동 (음수 비중→0%)
3. **Kelly 하드코딩 제거**: mu/sigma를 실제 수익률에서 계산
4. **팩터→BL 자동 뷰**: factor_to_views.py (수동 1개→자동 4개)
5. **상관관계 모니터**: correlation_monitor.py (상관 폭발 감지)
6. **재정규화 버그 수정**: 숏이 있었을 때만 재정규화

### Git 커밋 (pollmap/open-trading-api)
- `4183fdd` feat: quant risk management system v0.1α
- `af37e7d` fix: remove hardcoded mu/sigma in Kelly
- `7d50b8f` docs: ARCHITECTURE.md (491줄)
- `b823763` fix: portfolio-level vol targeting + auto short clipping
- `1a26b31` feat: auto factor-to-BL-views conversion
- `de69533` feat: correlation monitor + pipeline integration

### 코드 구조
```
kis_backtest/
├── core/pipeline.py              ★ QuantPipeline (E2E)
├── strategies/risk/
│   ├── cost_model.py              거래비용 + Kelly
│   ├── drawdown_guard.py          DD + 집중도
│   ├── vol_target.py              EWMA + 터뷸런스
│   └── correlation_monitor.py     ★ 상관 모니터 (NEW)
├── portfolio/
│   ├── mcp_bridge.py              MCP→KIS
│   ├── mcp_connector.py           MCP 정규화
│   ├── review_engine.py           주간 복기
│   └── factor_to_views.py         ★ 팩터→BL 뷰 (NEW)
└── tests/ (53/53 PASS)
```

### 추가 산출물
- `ARCHITECTURE.md` (491줄) — 전체 설계 문서
- `~/.claude/hooks/session_start.py` — 환경 자동 점검
- `~/.claude/hooks/validate_quant.py` — pytest 자동
- `~/Desktop/luxon-scripts/` — 배치 스크립트 2개
- `~/Desktop/luxon-context-for-claude-web.md` — 웹 Claude용 컨텍스트

### 다음 세션
1. DART 재무 데이터 → factor_score에 value/quality 추가
2. 벤치마크(KOSPI200) 실데이터 자동 수집 → 복기 정확도
3. KIS 모의투자 첫 주문
4. VPS/Obsidian/에이전트 전체 최신화 + README

**Why:** 기술적+매크로+정성+정량+퀀트+포트폴리오+리스크가 유기적으로 작동하는 시스템
**How to apply:** `pipeline.run()` 한 줄로 전체 실행. 공매도 클리핑/vol 타겟팅/상관 모니터/팩터→BL 전부 자동.
