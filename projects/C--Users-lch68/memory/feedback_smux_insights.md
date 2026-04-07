---
name: smux/tmux-bridge 세션 핵심 인사이트 5건
description: 멀티AI 오케스트레이션, MCP 래핑, 서브에이전트 메모리, OpenClaw MCP 설정, session lock 근본원인
type: feedback
---

## 1. smux/tmux-bridge = 멀티 AI CLI 오케스트레이션 도구
Codex(GPT) + Claude Code를 같은 tmux에서 동시 운용 가능. 한 AI가 다른 AI 화면을 직접 읽고 타이핑 가능. 에이전트 전용이 아니라 CLI 접근만 되면 누구든 사용 가능.

**Why:** 기존 MCP 통신은 구조화된 API 호출만 가능했지만, tmux-bridge는 "상대 터미널 화면 자체를 읽고 직접 키 입력"이라는 완전히 다른 레벨의 상호작용.
**How to apply:** 같은 머신 내 빠른 AI간 협업 → tmux-bridge. 구조화 데이터/크로스머신 → MCP.

## 2. MCP 서버로 감싸면 에이전트 자율 통신 가능
tmux-bridge CLI를 FastMCP 서버로 감싸면 에이전트가 `tmux_send("oracle", "분석해줘")` 한 줄로 호출. Read-Act-Read 사이클을 서버가 자동 처리.

**Why:** 에이전트가 bash로 4단계 명령을 직접 관리하면 실수 가능성 높음. MCP tool 하나로 추상화하면 안전하고 간편.
**How to apply:** 새 CLI 도구를 에이전트에 연동할 때 "MCP 서버로 감싸기" 패턴 우선 고려.

## 3. 서브에이전트는 메모리 거의 안 먹는다
OpenClaw 서브에이전트는 별도 프로세스가 아니라 같은 gateway 내 세션. 추가 메모리 수MB. 비용은 VPS 리소스가 아니라 Anthropic API 호출.

**Why:** 처음에 "서브에이전트 1개 = 50-100MB"로 잘못 추정 → 실제 측정하니 gateway 프로세스 내 세션이라 거의 무시 가능.
**How to apply:** 서브에이전트 수 제한은 메모리가 아니라 API 비용/rate limit 기준으로 판단.

## 4. OpenClaw MCP 설정은 mcporter.json(mcpServers)만 건드려라
`openclaw.json`에 `mcp.servers` 넣으면 "expected record, received array" 에러로 에이전트 크래시. 키 이름은 `mcpServers`(servers 아님).

**Why:** NEXUS 장애로 실전 발견 (2026-03-28). openclaw.json과 mcporter.json의 역할이 다름.
**How to apply:** MCP 서버 추가/제거 → `/root/{agent}-home/.mcporter/mcporter.json` 편집. openclaw.json에 mcp 키 있으면 즉시 제거.

## 5. session lock 근본 원인 = 비대한 세션 파일
디스코드 대화가 쌓이면 세션 파일이 수백KB~수MB. 파일 I/O 시 lock 10초 timeout 초과 → 에러. 재시작해도 stale lock 남으면 반복.

**Why:** NEXUS가 디스코드에서 반복적으로 session lock 에러 발생. gateway 중복이 아니라 세션 파일 크기가 근본 원인.
**How to apply:** 500KB+ 세션 주기적 아카이브. stale lock cron 5분마다 정리 (`/root/cleanup-stale-locks.sh`). 에이전트 재시작 전 반드시 `rm -f sessions/*.lock`.
