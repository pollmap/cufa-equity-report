---
description: "OpenClaw 서브에이전트 추가 — 메인 에이전트에 새 서브에이전트 등록"
---

# Subagent Add

메인 에이전트(HERMES/NEXUS/ORACLE)에 새 서브에이전트를 추가할 때 사용.

## 입력
$ARGUMENTS: {메인에이전트} {서브에이전트ID} {역할설명}

## 절차

1. 메인 에이전트 openclaw.json 읽기
   - HERMES: `/root/hermes-home/.openclaw/openclaw.json`
   - NEXUS: `/root/nexus-home/.openclaw/openclaw.json`
   - ORACLE: `/root/oracle-home/.openclaw/openclaw.json`

2. `agents.list` 배열에 새 서브에이전트 추가:
```json
{
  "id": "{서브에이전트ID}",
  "workspace": "/root/{에이전트}-home/.openclaw/workspace-{서브에이전트ID}",
  "identity": {
    "name": "{서브에이전트이름}",
    "theme": "{역할설명}"
  },
  "sandbox": {
    "mode": "all",
    "workspaceAccess": "rw",
    "scope": "agent"
  },
  "tools": {
    "deny": ["sessions_spawn", "subagents"]
  }
}
```

3. workspace 디렉토리 생성: `mkdir -p /root/{에이전트}-home/.openclaw/workspace-{서브에이전트ID}`

4. SOUL.md 작성 (역할, Vault 저장 규칙, 정책 필터)

5. vault_server.py에 쓰기 권한 추가

6. 에이전트 재시작: `systemctl restart openclaw-{에이전트}`
   - NEXUS는 `fuser -k 18790/tcp` 후 재시작

7. 검증: 어댑터에서 에이전트 목록 확인
