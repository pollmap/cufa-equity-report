---
name: Luxon 투자 트레이딩 시스템 로드맵
description: 퀀트×가치투자 하이브리드 — 5레이어 중 4개 이미 구현됨! 연결만 하면 됨
type: project
---

## 핵심 발견 (2026-04-04)

**KIS open-trading-api 플러그인이 생각보다 훨씬 완성도가 높음!**
Phase B~D로 계획했던 것들이 이미 구현되어 있음:

| 계획 | 실제 상태 | 위치 |
|------|----------|------|
| Phase B: 포트폴리오 관리 | ✅ 이미 있음 | `kis_backtest/portfolio/{analyzer,rebalance,visualizer}.py` |
| Phase C: 모의투자 실행 | ✅ 이미 있음 | `kis-order-executor` 스킬 + `strategy_builder/core/order_executor.py` |
| Phase D: 트레이드 저널 | ✅ 이미 있음 | `kis-trade-log.sh` 훅 (자동 기록) |
| Trading MCP | ✅ 이미 있음 | `MCP/KIS Trading MCP/` (시세+계좌+주문) |
| 보안 가드 | ✅ 이미 있음 | `kis-secret-guard.sh` + `kis-prod-guard.sh` |

## 수정된 로드맵

**새로 만들 것이 아니라 "연결"하면 됨:**

| Phase | 내용 | 상태 |
|-------|------|------|
| A | 전략 선택/추가 UX (SKILL.md Step 0) | ✅ 완료 |
| B' | CUFA 보고서 → `kis-order-executor` 연결 | 다음 세션 |
| C' | Trading MCP + 백테스트 MCP 동시 활용 파이프라인 | 다음 세션 |
| D' | Vault 트레이드 저널 연동 (기존 로그 → Vault MD) | 다음 세션 |
| E | 업비트 클라이언트 구현 (유일하게 없는 것) | 이후 |

## KIS 플러그인 4대 스킬

1. **kis-strategy-builder** — 전략 설계 (83지표, 66캔들, 10프리셋)
2. **kis-backtester** — 백테스트 (Lean Docker, MCP 11도구)
3. **kis-order-executor** — 주문 실행 (시그널→매수/매도, 강도 0.5 이상만)
4. **kis-team** — 전체 파이프라인 오케스트레이션 (1→2→3 순차)

## 없는 것 (만들어야 할 것)

- 업비트 API 클라이언트 (키는 있지만 코드 없음)
- CUFA 보고서 → 포트폴리오 편입 자동 연결
- Vault 트레이드 저널 (기존 로그→MD 변환)

**Why:** Zack Shapiro 로펌처럼 전문가 판단을 AI 스킬로 인코딩 → 1인 투자 회사
**How to apply:** Phase B'~D'는 "연결" 작업 — 새로 만들지 말고 기존 컴포넌트를 파이프라인으로 엮기
