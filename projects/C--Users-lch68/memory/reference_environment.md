---
name: 개발 환경 및 인프라
description: 2대 노트북(Lenovo 메인 + GalaxyBook WSL) + VPS + 도구 버전 + API 키 발급처
type: reference
---

## 메인 노트북 — LENOVO 83HY (현재 작업 기기)
- **CPU**: AMD Ryzen AI 7 350 (8C/16T + XDNA NPU)
- **RAM**: 32GB (31.3GB usable)
- **GPU**: AMD Radeon 860M (iGPU, 512MB VRAM)
- **OS**: Windows 11 Home
- **용도**: 주 개발, Claude Code, OpenClaude, Docker, 모든 작업

### 설치된 도구
| 도구 | 버전 | 용도 |
|------|------|------|
| Claude Code | 2.1.92 | Anthropic 원본 코딩 에이전트 |
| OpenClaude | 0.1.8 | 멀티모델 코딩 에이전트 (GPT-5.x) |
| Codex CLI | 0.118.0 | OpenAI OAuth 토큰 관리 |
| Ollama | 0.20.2 | 로컬 LLM 추론 (모델 미다운) |
| Node.js | v24.13.1 | |
| Python | 3.14.3 | |
| Git | 2.53.0 | |
| Docker | 29.3.1 | |
| ripgrep | 15.1.0 | |

### 쉘 설정 (~/.profile)
- `oc` / `oc5` / `oc3` / `ocds` — OpenClaude 별칭
- `oc-model` / `oc-status` / `oc-refresh` — 헬퍼 함수
- `gl` — gitlawb WSL 래퍼
- `vps` — SSH 별칭

## WSL2 (레노버 내부 — 같은 기기)
- **OS**: Ubuntu 24.04 (WSL2, Lenovo 내부)
- **도구**: gitlawb CLI v0.3.8, Node v22.22.1, Python 3.12.3, Git 2.43.0
- **gitlawb DID**: `did:key:z6Mkk8VikHH7mm5UCCrVr5jFrzyKk7enGt2fTGYCq4bQFrF7`
- **접속**: `wsl -d Ubuntu-24.04`

## Galaxy Book2 Pro (별도 기기)
- **용도**: WSL 전용 기기 (별도 운용)
- SSH: `valuealpha@10.0.0.2`
- 이번 세션에서 미사용

## VPS — Contabo (62.171.141.206)
- **OS**: Ubuntu 24.04.4 LTS
- **RAM**: 8GB / **CPU**: 4 cores / **Disk**: 112GB free
- **SSH**: `ssh -i ~/.ssh/cbnupollmap root@62.171.141.206` 또는 `ssh luxon claude`

### 에이전트 (v4.1, 2에이전트 VPS + 1에이전트 WSL)
| 에이전트 | MBTI | 포트 | 위치 | 상태 |
|---------|------|------|------|------|
| HERMES | ENTJ | 18789 | VPS | active |
| NEXUS | ENFJ | 18790 | VPS | active |
| DOGE | INTP | 18794 | WSL | WSL only |

### MCP v8.0-phase12
- 64 서버 / 364 도구 / 실패 0
- 헬스: `curl http://127.0.0.1:8100/health`
- nginx active / docker active

### SOUL.md 위치
- `/root/hermes-home/.openclaw/workspace/SOUL.md`
- `/root/nexus-home/.openclaw/workspace/SOUL.md`

### Obsidian Vault
- 위치: `/root/obsidian-vault/` (PARA 구조)
- 노트: 1,333개
- git 자동 커밋 (PostToolUse 훅)

## MCP 서버 (로컬 .mcp.json)
| 서버 | 타입 | URL/명령 | 도구 수 |
|------|------|---------|--------|
| drawio | HTTP | https://mcp.draw.io/mcp | 다이어그램 |
| kis-backtest | HTTP | http://127.0.0.1:3846/mcp | 백테스트 |
| nexus-finance | HTTP | http://62.171.141.206/mcp (Bearer) | 364 |
| gitlawb | stdio | wsl -- gl mcp serve | 40 |

## 인증
- **Anthropic**: API 키 (Claude Code)
- **OpenAI/ChatGPT**: Pro OAuth (`~/.codex/auth.json`, 자동 리프레시)
- **gitlawb**: DID + Ed25519 키 (`~/.gitlawb/identity.pem` in WSL)

## 무료 API 키 발급처

| API | 제한 |
|-----|------|
| ECOS (ecos.bok.or.kr) | 일 10만 |
| DART (opendart.fss.or.kr) | 일 1만 |
| KOSIS (kosis.kr) | 일 1만 |
| FRED (fred.stlouisfed.org) | 무제한 |
| Etherscan (etherscan.io) | 일 10만, 5/sec |
| Naver (developers.naver.com) | 일 2.5만 |
| Finnhub (finnhub.io) | 60/min |
| EIA (eia.gov/opendata) | 무제한 |
| 키 불필요 | ccxt, DefiLlama, Polymarket, GDELT, arXiv, OpenAlex, Open-Meteo, UN Comtrade |
