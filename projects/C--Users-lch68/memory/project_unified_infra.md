---
name: project_unified_infra
description: Luxon 통합 인프라 — 스킬 git sync + Obsidian 통합 두뇌 + SQLite 영구 기억 (Phase 3 대기)
type: project
---

# Luxon 통합 인프라 현황 (2026.03.27)

## Phase 1: 스킬/커맨드 자동 동기화 — 완료
- VPS bare repo: `/root/claude-skills-sync.git`
- Windows: `~/.claude/` → git repo, remote=VPS
- WSL: `~/claude-skills-local/` → clone, symlink to `~/.claude/`
- VPS Claude Code: `/root/.claude/skills` → symlink to `/root/claude-skills-local/skills`
- OpenClaw 에이전트(HERMES/NEXUS/ORACLE): symlink 연결됨
- `/sync-skills` 커맨드 생성됨
- git config core.sshCommand 설정으로 SSH 키 자동 사용

**Why:** 스킬을 한 환경에서 만들면 수동 복사 필요 없이 git push/pull로 전체 동기화

**How to apply:** 스킬 추가/수정 후 `/sync-skills` 실행, 또는 수동으로 `cd ~/.claude && git add -A && git commit && git push`

## Phase 2: Obsidian 통합 두뇌 — 완료
- VPS Vault: `/root/obsidian-vault/` (마스터, 158+ 노트)
- Windows: `~/obsidian-vault/` (clone)
- WSL DOGE: rsync 매시간 동기화 (VPS 크론)
- GitHub remote: `pollmap/luxon-vault` (자동 push)
- 자동화: sync_memory_to_vault, push_vault_to_wsl, dashboard_builder, auto_archive, brief_to_inbox, git auto-commit
- ai-workspace/ 구조 추가: outputs, sessions, research, decisions
- agents/ 구조: hermes, nexus, oracle, doge

## Phase 3: SQLite + 로컬 임베딩 영구 기억 — 완료 (2026.03.27)
- Frimion 방식: SQLite + Ollama bge-m3 + 하이브리드 검색(벡터+BM25+RRF)
- WAL 프로토콜: 응답 전 저장
- Superseded 마킹: 오래된 팩트 자동 교체
- MCP 서버로 구현 예정 (VPS 세션에서)
- 컨텍스트 262줄 유지 원칙 (줄이면 오히려 품질 하락)
