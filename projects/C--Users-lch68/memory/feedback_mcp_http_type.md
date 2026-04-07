---
name: MCP 원격 서버 type은 http
description: Claude Code 2.1.92+ MCP 원격 서버 설정 시 type은 반드시 "http", hooks는 PascalCase
type: feedback
---

MCP 원격 서버 type은 반드시 `"http"` 사용. `"url"`, `"sse"`, `"streamable-http"` 전부 스키마 검증 실패.

**Why:** Claude Code 2.1.92에서 `"http"`가 SSE와 Streamable HTTP를 모두 포괄하는 통합 타입으로 변경됨. `"sse"`는 문서에 존재하지만 실제 스키마 검증에서 거부됨.

**How to apply:**
- `.mcp.json` 또는 `.claude.json`에서 원격 MCP 서버 설정 시 `"type": "http"` + `"url"` 조합 사용
- hooks 이벤트명은 반드시 **PascalCase**: `PreToolUse`, `PostToolUse`, `Stop` (camelCase 거부됨)
- hooks 내부 구조: `hooks: [{ type: "command", command: "..." }]` 래핑 필수
