---
name: 44세션 인사이트 분석 + 개선 적용 (2026.04.05)
description: 86세션/68시간 분석 — wrong_approach 40회, buggy_code 33회, encoding 반복. CLAUDE.md+Hook+품질게이트 개선 적용
type: feedback
---

# Claude Code Insights 분석 결과 (86세션, 44분석)

## 반복 마찰 TOP 3 + 적용한 해결책

### 1. wrong_approach (40회) — 범위 이탈/잘못된 접근
- "내 파트만 집중해서!!!!!!!!!" 사건
- MCP 안 쓰고 직접 리서치, 전체 팀 분석, 파일 분할 등
- **해결**: CLAUDE.md에 "범위 엄수", "MCP 도구 우선", "접근법 먼저 확인" 규칙 추가됨
- **추가 개선**: 세션 시작 시 "Task/Scope/Constraints" 명시 템플릿 사용

### 2. buggy_code (33회) — 서브에이전트 버그/빈출력
- 빈 SVG, 하드코딩 흰 배경, 30K자(목표 50K+), 스킬 규칙 무시
- **해결**: CLAUDE.md에 "3-에이전트 코드 가드", "서브에이전트 계약서" 규칙
- **추가 개선**: 서브에이전트 스폰 시 핵심 규칙 3줄 직접 명시

### 3. encoding (cp949/경로) — 반복 환경 문제
- cp949 가정, Windows 경로, WSL2 인코딩 불일치
- **해결**: CLAUDE.md에 "encoding='utf-8' 명시", "cp949 절대 가정 금지"
- **추가 개선**: Hook으로 파일 쓰기 후 utf-8 검증 자동화

## 추천 기능 + 적용 상태

| 기능 | 상태 | 설명 |
|------|------|------|
| Hooks (postEdit utf-8 검증) | TODO | 파일 쓰기 후 인코딩 자동 체크 |
| Hooks (postCommit 테스트) | TODO | 커밋 후 pytest 자동 실행 |
| Headless Mode (배치 보고서) | TODO | 288개 보고서 배치 생성 |
| Phase 체크포인트 | 적용됨 | CLAUDE.md에 "3 Phase 이상이면 단계별 게이트" |
| 서브에이전트 품질 게이트 | 적용됨 | CLAUDE.md에 4단계 검증 |
| MCP 우선 규칙 | 적용됨 | CLAUDE.md + feedback_mcp_first.md |

## 핵심 수치
- 세션당 평균 6메시지, 1.5시간
- 불만족 31회/149 감정신호 (21%)
- 15커밋/44세션 (세션당 0.34커밋)
- Agent 호출 132회, TaskUpdate 113회, Bash 637회

**Why:** 반복 마찰 패턴을 구조적으로 해결해야 세션 효율 극대화
**How to apply:** 세션 시작 시 이 피드백 참고, Hook 설정으로 자동화, 서브에이전트에 규칙 직접 전달
