---
name: 다음 세션 TODO (2026-04-05~)
description: 리뷰 수정 진행 중 + Docker 의존성 발견, 남은 작업 정리
type: project
---

## 완료 항목 (이번 세션)

1. ~~`uv sync`~~ — KIS Python 환경 설정 ✅
2. ~~VPS MCP~~ — 이미 가동 중 ✅ (46서버/253도구)
3. ~~KIS 모의투자 인증~~ ✅ (토큰 만료: 2026-04-05 01:23:46)
4. ~~KIS 백테스터 MCP 시작~~ ✅ (127.0.0.1:3846, 11도구)
6. ~~백테스트 통합~~ ✅ — SKILL.md Phase 6.5 + build_template.py + .mcp.json

## 리뷰 수정 진행 중

- [x] Step 4: build_template.py (appendix_16 수정, html.escape 추가)
- [x] Step 5: skill.meta.json v13.2 업데이트
- [x] Step 3: backtest_result_table() 단위 테스트 통과 (XSS 방어 확인)
- [ ] Step 1+2: SKILL.md DOCX 삭제 + 섹션 번호 수정 (에이전트 진행 중)
- [ ] Step 3: E2E 백테스트 실행 → **Docker Desktop 필요** (찬희 수동 시작)

## 남은 작업

1. **Docker Desktop 시작** → 삼성전자 백테스트 E2E 테스트 재시도 (찬희 수동)
2. **이노스페이스(462350) 보고서 실전 빌드** — v13.2 첫 테스트
3. **업비트 API 키 재발급** (매매 권한 추가)
4. **한투+업비트 키 재발급** (보안 — 채팅에 노출됨)
5. **NEXUS 디스코드 2번 답하는 문제** 해결

## 새로 발견된 의존성

- **KIS 백테스트 = Docker 필수**: QuantConnect Lean 엔진이 Docker 컨테이너에서 실행됨
  - MCP 서버 자체는 Docker 없이도 가동 (health/tools/list OK)
  - 실제 백테스트 실행(run_backtest) 시 Docker Desktop 필요
  - 에러: "Docker가 실행되지 않습니다. Docker Desktop을 시작해주세요."

## 환경 정보

- KIS open-trading-api: `~/Desktop/open-trading-api/`
- KIS config: `~/KIS/config/kis_devlp.yaml` (모의투자만)
- MCP 서버: drawio (원격) + kis-backtest (로컬:3846) + Nexus MCP (VPS:8100)
- 백테스트 실행 조건: Docker Desktop 실행 중이어야 함

**Why:** Phase 6.5 백테스트 E2E 검증이 Docker 없이는 불가능
**How to apply:** 다음 세션 시작 시 Docker Desktop 먼저 확인, 그다음 백테스트 E2E 테스트
