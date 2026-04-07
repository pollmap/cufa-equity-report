---
name: smux tmux-bridge MCP 인프라
description: VPS smux+tmux-bridge MCP(8101) 6tool 완료, Codex 인증, 검증 PASS, Vault 저장됨
type: project
---

## smux (tmux-bridge) 설치 현황 (2026-03-28)

**Why:** 같은 VPS 내 에이전트 간 MCP 없이 빠른 직접 통신 가능. 에이전트가 CLI이므로 tmux-bridge 커맨드 직접 실행 가능.

**How to apply:** 에이전트 간 빠른 소통은 tmux-bridge, 구조화 데이터/크로스 머신은 MCP.

### VPS 설치 완료
- smux v1.0.0: `~/.smux/` (tmux.conf, bin/tmux-bridge, bin/smux)
- PATH: `/root/.smux/bin` → `.bashrc`에 추가됨
- SSH에서 사용 시: `export TMUX_BRIDGE_SOCKET=/tmp/tmux-0/default`

### tmux 세션 구조
```
세션: luxon (4 windows)
├── hermes (pane %0) — /root/hermes-home
├── nexus  (pane %1) — /root/nexus-home
├── oracle (pane %2) — /root/oracle-home
└── monitor (pane %3) — MCP health watch
```

### 배포 내역
- smux 스킬: `/root/{agent}-home/.claude/skills/smux/` (SKILL.md + references)
- SOUL.md: 각 에이전트에 tmux-bridge 섹션 추가 (동료 테이블 + Read-Act-Read 사용법)
- 자동 시작: `/root/luxon-tmux-init.sh` + `luxon-tmux.service` (systemd enabled)

### 스킬
- `smux-remote` 스킬 생성 완료: `~/.claude/skills/smux-remote/` (SKILL.md + references/quick-commands.md)
- VPS 3개 에이전트에도 원본 smux 스킬 배포: `/root/{agent}-home/.claude/skills/smux/`

### tmux-bridge MCP 서버
- FastMCP 3.1.1 기반, 포트 8101 (127.0.0.1)
- 6개 tool: tmux_list, tmux_read, tmux_send, tmux_exec, tmux_keys, tmux_status
- systemd: `tmux-bridge-mcp.service` (enabled, active)
- 코드: `/root/tmux-bridge-mcp/server.py`
- 3개 에이전트 mcporter에 등록 완료
- SOUL.md에 MCP tool 사용법 추가 완료
- 에이전트 재시작 완료

### Codex CLI
- VPS에 Codex CLI v0.115.0 설치됨, ChatGPT Pro 인증 (`~/.codex/auth.json`)
- 모델: gpt-5.4
- hermes pane에서 실행 테스트 완료

### 감사 완료 (2026-03-28)
- auth.json/env 권한 600 수정 (CRITICAL)
- server.py docstring 보강, exception 범위 축소, timeout 메시지 수정
- requirements.txt 중복 정리
- 최종 검증: 6개 서비스 active, 6개 tool 전체 OK, 보안 OK

### 저장 현황
- Obsidian Vault: `03-Resources/infrastructure/smux-tmux-bridge-mcp.md`
- 에이전트 memory: `/root/{agent}-home/.openclaw/workspace/memory/smux-tmux-bridge.md`
- Windows 스킬: `~/.claude/skills/smux-remote/`
- Windows 메모리: 이 파일

### 미완료 (Phase 2-3)
- WSL(DOGE): 노트북 켜졌을 때 설치
- 크로스 머신 SSH 터널: 검토 예정
