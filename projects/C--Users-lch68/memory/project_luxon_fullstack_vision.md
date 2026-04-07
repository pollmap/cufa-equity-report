---
name: AI 헤지펀드 풀스택 비전
description: 1인 AI 운용사 — MCP 364도구 + CUFA 보고서 + LEAN/KIS 실행, 실전 투자 예정 (2026.04.04 확정)
type: project
---

# AI 헤지펀드 풀스택 비전 (2026.04.04 업데이트)

Luxon = 1인 AI 퀀트/가치투자 운용사. **실전 투자 진행 예정.**

## 3대 무기 (최신 상태)

| 무기 | 위치 | 상태 | 역할 |
|------|------|------|------|
| Nexus MCP v8.0 | VPS 127.0.0.1:8100 (**364도구/64서버**) | 실전 가동 | 데이터+분석+시그널+포트폴리오+실행최적화 |
| CUFA 보고서 v14.1 | `pollmap/cufa-equity-report` (GitHub) | 실전 가동 | 기업분석 → DCF → 시나리오 → Kill Conditions |
| LEAN/KIS 자동매매 | `~/Desktop/open-trading-api/backtester/` | 리서치 단계 | 백테스트 → 자동매매 주문 실행 |

## /quant-fund 스킬 완성 (2026.04.04)

- 7단계 파이프라인: 유니버스 → 시그널 → 포트폴리오 → 리스크 → 실행 → 모니터링 → 리포트
- 6종 전략 프리셋: 한국 멀티팩터, 페어 트레이딩, 글로벌 매크로, 크립토 캐리, 볼 타이밍, ML 멀티알파

## 합체 파이프라인

분석(CUFA) → 퀀트 시그널(MCP 364도구) → 포트폴리오 최적화(BL/HRP) → 리스크 관리 → 백테스트(LEAN/KIS) → 실행(KIS API) → 복기(보고서)

## 실전 투자 원칙 (찬희 확인)

- **신중하고 전략적이고 실용적인 태도** 필수
- 모의투자 → 소액 실전 → 검증 후 증액 (점진적 배포)
- 리스크 관리 > 알파 추구
- 백테스트 과최적화 경계

## LEAN 위치

- 워크스페이스: `~/Desktop/open-trading-api/backtester/.lean-workspace/`
- KIS 백테스트 엔진: `kis_backtest/` (strategies, codegen, lean, portfolio, report)
- KIS MCP 서버: `kis_mcp/` (127.0.0.1:3846)

## 다음 세션 TODO

1. 노트북 Claude Code에 MCP 연결 설정 (settings.json에 nexus-finance 추가)
2. /quant-fund 스킬 실전 테스트 — 한국 멀티팩터 프리셋으로 첫 분석
3. KIS MCP 활용 스킬 생성 — kis-backtest MCP(3846)를 퀀트 파이프라인과 연결
4. LEAN 통합 설계 — 백테스트→실행 단계 구체화

**Why:** 찬희가 실제 투자를 진행할 예정이므로 모든 퀀트 도구/스킬 작업에서 실전 리스크를 항상 고려
**How to apply:** 퀀트 분석 결과 제시 시 항상 한계점/리스크 명시, 과최적화 경고, 포지션 사이징 권고 포함
