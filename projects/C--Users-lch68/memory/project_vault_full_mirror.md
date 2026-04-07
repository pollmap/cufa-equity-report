---
name: project_vault_full_mirror
description: Vault 풀 미러링 완료 — CLAUDE.md, 커맨드, 메모리, settings, SOUL.md 전부 Obsidian에 미러
type: project
---

# Vault 풀 미러링 (완료 2026-03-27)

## 결과

| 항목 | 개수 | Vault 경로 |
|------|------|-----------|
| CLAUDE.md | 1 | `ai-workspace/config/CLAUDE.md` |
| 커맨드 | 29 | `ai-workspace/config/commands/` |
| 메모리 | 28 | `ai-workspace/config/memory/` |
| settings | 2 | `ai-workspace/config/settings/` (API키 마스킹) |
| SOUL.md | 4 | `agents/{hermes,nexus,oracle,doge}/SOUL.md` |
| MOC 인덱스 | 1 | `ai-workspace/config/CONFIG-MOC.md` |

## 동기화 스크립트
`obsidian-vault/scripts/mirror_config_to_vault.sh` — 재실행 가능, SSH로 VPS/WSL SOUL.md 자동 가져옴.

**Why:** 모든 지식이 Vault에 있어야 Obsidian 검색/열람 가능
**How to apply:** 설정 변경 시 `bash ~/obsidian-vault/scripts/mirror_config_to_vault.sh` 재실행
