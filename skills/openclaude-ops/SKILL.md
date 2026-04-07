---
name: openclaude-ops
description: OpenClaude + gitlawb 운영 스킬. 멀티모델 관리, MCP 서버 제어, gitlawb 에이전트 관리, VPS 연동, 토큰 리프레시. 트리거 — 'openclaude', 'gitlawb', '모델 전환', 'MCP 관리', 'DID', '에이전트 라우팅'
version: 1.0.0
triggers:
  - openclaude
  - gitlawb
  - 모델 전환
  - model switch
  - MCP 관리
  - agent routing
  - DID
  - 토큰 갱신
---

# OpenClaude + gitlawb 운영 스킬

## CRITICAL: --bare 모드 필수

OpenClaude에서 203개 스킬을 전부 로드하면 GPT-5.x 컨텍스트 윈도우를 초과한다 (API Error 500).
반드시 `--bare` 모드로 실행하고, 경량 시스템 프롬프트만 로드해야 한다.

```bash
# 올바른 사용법 (별칭 oc가 이미 설정됨)
oc                    # --bare + system-prompt-file 자동 적용
oc-raw                # 시스템 프롬프트도 없는 순수 bare 모드
oc-full               # 전체 모드 (GPT-5에서 크래시 가능, Claude Code 전용)
```

경량 시스템 프롬프트: `~/.claude/openclaude-system-prompt.md`
- 찬희 작업 스타일 + 환경정보 + MCP 핵심만 포함
- 스킬/커맨드/메모리 자동 로드 안 됨

## 1. 멀티모델 관리

### 현재 모델 설정
- **codexspark** (GPT-5.3): 기본, 항상 사용 가능
- **codexplan** (GPT-5.4): 주간 한도 있음, 고난도 작업용
- **DeepSeek**: API 키 필요, 탐색/리서치용
- **Ollama**: 로컬, 무료, 오프라인 가능

### 모델 전환 방법

```bash
# 쉘에서
oc-model 5.4     # GPT-5.4로 전환
oc-model 5.3     # GPT-5.3으로 전환
oc-model ds      # DeepSeek로 전환
oc-model local   # Ollama 로컬로 전환

# --bare 모드 별칭 (필수, 위 CRITICAL 섹션 참조)
oc                # --bare + system-prompt-file 자동 적용 (기본 사용법)
oc-raw            # 시스템 프롬프트도 없는 순수 bare 모드
oc-full           # 전체 모드 (GPT-5에서 크래시 가능, Claude Code 전용)

# 모델별 별칭
oc5              # GPT-5.4로 OpenClaude 실행
oc3              # GPT-5.3으로 OpenClaude 실행
ocds             # DeepSeek로 OpenClaude 실행
```

### 에이전트 라우팅 (settings.json)
```json
{
  "agentRouting": {
    "Plan": "codexplan",        // 고난도 → GPT-5.4
    "architect": "codexplan",
    "security-reviewer": "codexplan",
    "Explore": "codexspark",   // 일반 → GPT-5.3
    "general-purpose": "codexspark",
    "default": "codexspark"
  }
}
```

## 2. gitlawb 에이전트 관리

### 신원 정보
- **DID**: `did:key:z6Mkk8VikHH7mm5UCCrVr5jFrzyKk7enGt2fTGYCq4bQFrF7`
- **Key**: `~/.gitlawb/identity.pem` (WSL2)
- **Trust**: 0.05 (활동으로 성장)
- **UCAN 만료**: 2026-05-07 (만료 전 `gl register` 재실행)

### gitlawb 명령어 (Windows에서 WSL 래퍼)
```bash
gl repo list                    # 리포 목록
gl repo create NAME             # 리포 생성
gl mirror URL                   # GitHub → gitlawb 미러
gl issue create -t TITLE REPO   # 이슈 생성
gl issue list REPO              # 이슈 목록
gl pr create ...                # PR 생성
gl bounty list                  # 바운티 목록
gl agent list                   # 네트워크 에이전트 목록
gl node status                  # 노드 상태
gl changelog REPO               # 변경 이력
gl doctor                       # 시스템 점검
```

### gitlawb MCP 도구 (40개)
Claude Code에서 자동 사용 가능:
- **신원**: identity_show, identity_sign, did_resolve
- **리포**: repo_create, repo_list, repo_get, repo_commits, repo_tree
- **PR**: pr_create, pr_list, pr_view, pr_diff, pr_review, pr_merge
- **이슈**: issue_list, issue_create, issue_comment
- **바운티**: bounty_list, bounty_create, bounty_claim, bounty_submit
- **태스크**: task_list, task_create, task_claim, task_complete
- **UCAN**: ucan_delegate, ucan_verify, ucan_show
- **웹훅**: webhook_create, webhook_list, webhook_delete
- **노드**: node_info, node_health

## 3. MCP 서버 관리

### 현재 MCP 서버 (`.mcp.json`)
| 서버 | 타입 | URL/명령 |
|------|------|---------|
| drawio | HTTP | https://mcp.draw.io/mcp |
| kis-backtest | HTTP | http://127.0.0.1:3846/mcp |
| nexus-finance | HTTP | http://62.171.141.206/mcp (Bearer) |
| gitlawb | stdio | wsl -- gl mcp serve |

### MCP 서버 추가 방법
```json
// .mcp.json에 추가
{
  "mcpServers": {
    "new-server": {
      "type": "http",
      "url": "http://...",
      "headers": { "Authorization": "Bearer ..." }
    }
  }
}
```

## 4. VPS 연동

### VPS 접속
```bash
vps                             # SSH 별칭
ssh luxon claude                # 노트북에서
```

### VPS 에이전트
| 에이전트 | 포트 | 역할 |
|---------|------|------|
| HERMES | 18789 | 수익 엔진 |
| NEXUS | 18790 | 데이터 허브 |
| DOGE | 18794 | 리서치 (WSL only) |

## 5. 토큰 관리

### 자동 리프레시
- Windows Task Scheduler: `LuxonCodexTokenRefresh` (매일 09:00)
- 스크립트: `~/.claude/scripts/refresh-codex-token.ps1`

### 수동 리프레시
```bash
oc-refresh          # codex auth login 실행
codex auth login    # 직접 실행
```

### 상태 확인
```bash
oc-status           # 모델/토큰/gitlawb 전체 상태
```

## 6. 트러블슈팅

| 문제 | 해결 |
|------|------|
| 토큰 만료 | `oc-refresh` 또는 `codex auth login` |
| 주간 한도 초과 | `oc-model 5.3` 또는 내일 17시 리셋 대기 |
| gitlawb 연결 실패 | `gl doctor` 확인, UCAN 만료 시 `gl register` |
| MCP 연결 안됨 | WSL 시작 확인: `wsl --list --verbose` |
| Ollama 안됨 | 터미널 재시작, `ollama serve` 실행 확인 |
