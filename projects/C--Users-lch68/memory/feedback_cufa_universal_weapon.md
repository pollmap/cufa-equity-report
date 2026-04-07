---
name: CUFA 보고서 파이프라인 = 범용 무기
description: CUFA 보고서 생성 도구를 Claude Code 뿐 아니라 OpenClaw/Codex 등 모든 에이전트에서 사용 가능한 범용 무기로 설계
type: feedback
---

CUFA 보고서 파이프라인은 특정 에이전트에 종속되지 않는 범용 도구여야 한다.

**Why:** 찬희의 비전 — build_template.py + config.py + gen_excel.py 구조가 Claude Code 뿐 아니라 OpenClaw, Codex, 기타 AI 에이전트에서도 돌아가야 한다. "무기"가 되는 것.

**How to apply:**
- 서브에이전트 의존 최소화, Claude Code 자체가 직접 실행
- 파이프라인의 각 단계를 독립 실행 가능한 Python 스크립트로 구현
- config.py = 데이터, build_template.py = 렌더링, gen_excel.py = 엑셀 — 3개 파일이 핵심
- 백테스트(KIS MCP)도 나중에 동일 구조로 통합
- 에이전트 불문 범용성: 표준 Python + HTML/CSS/JS만 사용, 특수 의존성 최소화
