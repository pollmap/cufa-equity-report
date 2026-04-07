---
name: Vault 업그레이드 v3.4
description: Desktop MCP 추가, 자동 브리핑 시스템, Vault 벡터 인덱싱, 에이전트 Vault 참조 규칙 — 5단계 업그레이드 완료
type: project
---

# Vault 업그레이드 v3.4 (2026-03-27)

## Phase 1: Claude Desktop에 local-vault MCP 추가
- `claude_desktop_config.json`에 3개 MCP: nexus-finance + local-vault + local-desktop
- Desktop에서 Vault 직접 읽기/쓰기 가능 (네트워크 없이도)

## Phase 2: 자동 브리핑 시스템 (3계층)
- **RemoteTrigger** `daily-ai-brief` (trig_01C2wfWmScxvWDBXrSqMwXYY): 매일 8:03 KST, VALU 환경, Crypto.com MCP, luxon-vault git repo
- **`/brief` 커맨드**: 수동 호출, 웹 검색 → Vault 00-Inbox에 저장
- **pull_vault_from_github.sh**: 트리거 결과 로컬 수신
- 트리거 관리: https://claude.ai/code/scheduled/trig_01C2wfWmScxvWDBXrSqMwXYY

## Phase 3: Vault 벡터 인덱싱
- `vault_index_server.py` → VPS 배포, Gateway에 29번째 서버로 등록
- 3개 도구: vault_index, vault_semantic_search, vault_related
- DB: /opt/nexus-finance-mcp/vault/vault_index.db (SQLite + bge-m3)
- 크론: 매 3시간 증분 인덱싱
- **systemd 수정**: ProtectHome=false, ReadWritePaths에 /root/obsidian-vault 추가

## Phase 4: 에이전트 SOUL.md Vault 참조 규칙
- HERMES/NEXUS/ORACLE/DOGE 전부 추가
- 작업 시작 전 vault_semantic_search → 과거 분석 참조 필수
- 작업 완료 후 vault_write → 인사이트 저장

## Phase 5: 크로스 앱 워크플로우 문서화
- `02-Areas/agent-ops/cross-app-workflow.md` 생성
- Desktop↔Code↔VPS↔WSL 전체 아키텍처 가이드

## 인프라 현황 (v3.4)
- MCP 서버: 29 (0 실패)
- MCP 도구: 139
- 커맨드: /brief 신규 (총 20개)

**Why:** 트위터에서 Filesystem MCP + Obsidian 연동 글 보고, 우리 인프라에서 더 뽑아낼 수 있는 것 5가지 발견
**How to apply:** /brief로 뉴스 수집, vault_semantic_search로 시맨틱 검색, Desktop에서 바로 Vault 접근
