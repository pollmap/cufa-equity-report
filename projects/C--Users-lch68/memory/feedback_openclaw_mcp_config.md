---
name: OpenClaw MCP 설정 규칙
description: MCP 서버는 mcporter.json(mcpServers 키)에서만 관리, openclaw.json에 mcp 키 넣지 말 것
type: feedback
---

OpenClaw 에이전트의 MCP 서버 설정은 반드시 `mcporter.json`의 `mcpServers` 키에서만 관리한다. `openclaw.json`에 `mcp.servers`를 넣으면 형식 오류(expected record, received array)로 에이전트가 죽는다.

**Why:** NEXUS 에이전트가 openclaw.json에 잘못된 mcp.servers(array)가 있어서 재시작 시 크래시 + session file lock 발생. 2026-03-28 실전에서 발견.

**How to apply:**
- MCP 서버 추가/제거: `/root/{agent}-home/.mcporter/mcporter.json` 편집
- 키 이름: `mcpServers` (servers 아님)
- `openclaw.json`에 `mcp` 키가 있으면 즉시 제거
- 에이전트 재시작 후 `journalctl -u openclaw-{agent} -n 10`으로 에러 확인
- lock 파일 잔존 시: `rm -f /root/{agent}-home/.openclaw/agents/*/sessions/*.lock`
