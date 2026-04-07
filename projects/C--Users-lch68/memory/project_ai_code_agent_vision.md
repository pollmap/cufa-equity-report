---
name: AI 코드 에이전트 풀스택 비전
description: 나만의 AI 코드 에이전트 시스템 — OpenClaude+gitlawb+Atomic Chat+Ollama 멀티모델, DID 신원, 에이전트 경제
type: project
---

## 비전: 나만의 AI 코드 에이전트 풀스택

### 핵심 컨셉
- 일반 개발자: GitHub + VS Code + ChatGPT = **도구를 쓰는 사람**
- 찬희의 방향: gitlawb + OpenClaude + DID = **에이전트가 일하는 시스템, 사람은 방향만 제시**

### 현재 달성도 (80%, 2026.04.07)

| 컴포넌트 | 상태 | 역할 |
|---------|------|------|
| OpenClaude v0.1.8 | 설치/동작 | 멀티모델 코딩 에이전트 CLI |
| ChatGPT Pro OAuth | 연동 완료 | GPT-5.3/5.4 무과금 사용 |
| 에이전트 라우팅 | 설정 완료 | 태스크별 모델 자동 배정 |
| gitlawb v0.3.8 | 등록/push | 탈중앙 Git + DID 신원 + 에이전트 경제 |
| gitlawb MCP 40도구 | 연동 완료 | PR/이슈/바운티/UCAN 자동화 |
| Ollama v0.20.2 | 설치 완료 | 로컬 추론 fallback (무료/오프라인) |
| Codex CLI 0.118.0 | 있었음 | OAuth 토큰 관리 |
| 토큰 자동 리프레시 | 크론 설정 | Task Scheduler 매일 09:00 |
| 스킬 203개 | 동작 중 | openclaude-ops 포함 신규 31개 |
| ~/.claude/ 공유 | 확인 | Claude Code/OpenClaude/Codex 3CLI 공유 |

### 미완성 (20%)

| 항목 | 필요 조건 | 시기 |
|------|----------|------|
| Atomic Chat | Win 버전 출시 대기 | 미정 |
| DeepSeek API | API 키 발급 | 필요시 |
| 바운티 자동화 | gitlawb 토큰 경제 성숙 | alpha 이후 |
| VPS OpenClaude 동기화 | 다음 세션 | 가까운 시일 |
| pm-skills-ko 65개 | 설치만 하면 됨 | 필요시 |

### 최종 목표
찬희가 자는 동안 에이전트(HERMES/NEXUS/DOGE)가:
1. gitlawb에서 바운티 claim
2. OpenClaude로 코드 작성
3. PR 제출 + 자동 리뷰
4. 스마트 컨트랙트로 자동 결제
→ DID + Trust Score = 신뢰 레이어

### 쉘 명령어 퀵 레퍼런스
- `oc` / `oc5` / `oc3` / `ocds` — OpenClaude (5.3/5.4/DeepSeek)
- `oc-model 5.4|5.3|ds|local` — 모델 전환
- `oc-status` — 전체 상태 확인
- `oc-refresh` — 토큰 수동 갱신
- `gl` — gitlawb CLI (WSL 래퍼)
