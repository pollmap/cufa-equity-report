---
name: Obsidian Vault Shared Brain
description: Obsidian vault is now the shared knowledge base for all Luxon agents via MCP vault_* tools
type: project
---

Obsidian Vault (/root/obsidian-vault)는 모든 에이전트의 공유 뇌로 설정됨.

**MCP Vault 도구 (6개)**: vault_search, vault_read, vault_list, vault_recent, vault_tags, vault_write
- 서버: /root/nexus-finance-mcp/mcp_servers/servers/vault_server.py
- Gateway에 26번째 서버로 등록

**에이전트 쓰기 권한**:
- VPS: HERMES(00-Inbox/hermes, 01-Projects), NEXUS(00-Inbox/nexus, 02-Areas), ORACLE(00-Inbox/oracle, 03-Resources)
- WSL: GATE(00-Inbox/gate, 01-Projects), CHIEF(00-Inbox/chief, 01-Projects), DOGE(00-Inbox/doge, 03-Resources)
- 모든 에이전트: 전체 읽기 가능

**vault_write → 자동 git commit + push**: 에이전트가 쓰면 즉시 GitHub 반영.
**Sync 크론**: 6시간마다 (0 */6 * * *) — 에이전트 메모리 → Vault 자동 동기화 + git push
**GitHub repo**: PRIVATE (pollmap/luxon-vault)

**Gateway 버그 수정**: FastMCP 3.x에서 _tool_manager._tools → _local_provider._components로 변경. 이전에 도구 0개 복사되던 버그 수정 → 126개 도구 정상 등록.

**Vault에 저장된 전략 문서**:
- 01-Projects/luxon-expansion-10-directions.md — 10방향 확장 전략 + 우선순위
- 01-Projects/luxon-expansion-prompts.md — 5개 Claude Code 실행 프롬프트
- 01-Projects/wsl-agent-vault-setup.md — WSL 에이전트 연결 가이드

**Why:** 사용자가 Obsidian을 "모든 에이전트와 나의 제2의 공유 뇌"로 만들고자 함. 에이전트 간 지식 공유가 핵심.
**How to apply:** 에이전트 관련 작업 시 vault 도구 활용 여부 고려. MCP 서버 추가 시 _local_provider._components 패턴 사용.
