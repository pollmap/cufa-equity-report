---
name: OpenClaude + gitlawb 설치 완료
description: OpenClaude v0.1.8 + gitlawb v0.3.8 풀 셋업, ChatGPT Pro OAuth, 에이전트 라우팅, 토큰 자동 리프레시
type: project
---

## OpenClaude v0.1.8 (2026.04.07 설치)

- **위치**: Windows npm global (`@gitlawb/openclaude`)
- **인증**: ChatGPT Pro OAuth (`~/.codex/auth.json`, VPS에서 복사)
- **모델**: codexspark (GPT-5.3) 기본, codexplan (GPT-5.4) 주간 리셋 후 전환
- **에이전트 라우팅**: Plan/architect/security → 5.4, 나머지 → 5.3 (`settings.json`)
- **토큰 자동 리프레시**: Windows Task Scheduler `LuxonCodexTokenRefresh` 매일 09:00
- **쉘 설정**: `~/.profile` — `oc`, `oc5`, `oc3`, `ocds` 별칭, `oc-model`, `oc-status` 함수

## gitlawb v0.3.8 (WSL2 Ubuntu 24.04)

- **DID**: `did:key:z6Mkk8VikHH7mm5UCCrVr5jFrzyKk7enGt2fTGYCq4bQFrF7`
- **Trust**: 0.05 (신규), UCAN 만료 2026-05-07
- **Repos**: luxon-test (docs), open-trading-api (GitHub 미러)
- **Issue**: #4923b186 (MCP integration)
- **MCP 연동**: `.mcp.json`에 WSL 래퍼로 추가 (`wsl -- gl mcp serve`)
- **쉘 별칭**: `gl` → `wsl -d Ubuntu-24.04 -- /home/lch68/.local/bin/gl`

## 스킬 추가 설치 (172 → 202)

- Superpowers 14개 (brainstorming, systematic-debugging, subagent-driven-development 등)
- AutoResearchClaw 9개 (a-evolve, researchclaw, scientific-writing 등)
- UI/UX Pro Max 7개 (design, brand, slides, ui-ux-pro-max 등)

## 다운로드 폴더 참고 자료

| 폴더 | 내용 | 가치 |
|------|------|------|
| everything-claude-code | ECC 하니스 (36에이전트/68커맨드/142스킬) | 레퍼런스 |
| claude-code-source-code | Claude Code v2.1.88 디컴파일 소스 | 아키텍처 참고 |
| claw-code | Python/Rust 재구현 | 학습용 |
| Superpowers | 13 프로덕션 스킬 | 설치 완료 |
| AutoResearchClaw | 논문 자동 생성 파이프라인 | 설치 완료 |
| ui-ux-pro-max-skill | 디자인 인텔리전스 | 설치 완료 |
| pm-skills-ko | PM 65스킬 한국어 | 미설치 (필요시) |
| Companion/Kanna | Claude Code 웹 UI | 참고용 |
| Paperclip | 멀티에이전트 제어판 | 참고용 |

## 법적 주의

OpenClaude는 Anthropic 비인가 포크. 실험/학습용 OK, 프로덕션 서비스 통합 시 리스크 평가 필요.
