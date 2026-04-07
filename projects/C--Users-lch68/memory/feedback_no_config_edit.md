---
name: 에이전트 인프라 보호 규칙 (2026-03-29 사고 종합)
description: openclaw.json 수정 금지 + 세션 비대화 방지 + DNS 안정화 + systemd 보호 — 전체 에이전트 동시 장애 방지
type: feedback
---

## 1. openclaw.json 수정 금지
에이전트에게 "설정 바꿔", "채널 추가해" 등을 지시하면 안 됨. 잘못된 키(`allowedGroups` 등) 추가 시 전체 crash loop.

**Why:** 2026-03-29 사고 — 4개 에이전트가 동시에 `allowedGroups` 키 추가 → 전원 crash loop

**How to apply:**
- 4개 에이전트 SOUL.md에 "⛔ 시스템 설정 수정 금지" 비협상 규칙 추가 완료
- OpenClaw 유효한 compaction mode: "default", "safeguard" 두 가지만
- config 수정은 찬희가 직접 하거나 Windows Claude Code에서 SSH로

## 2. 세션 비대화 방지
세션 .jsonl 파일이 1MB 넘으면 Anthropic long context rate limit (429) 발생 → 응답 불가

**Why:** HERMES 3.8MB, DOGE 5.3MB 세션으로 4개 에이전트 동시 멈춤

**How to apply:**
- VPS: `/root/cleanup_sessions.sh` 크론 30분마다 자동 정리
- WSL: `/home/lch68/cleanup_sessions.sh` 크론 30분마다 자동 정리
- SOUL.md에 "서브에이전트 우선 원칙" — 메인 세션 컨텍스트 최소화
- compaction mode: "default" (safeguard보다 적극적)

## 3. DNS 안정화
Contabo 기본 DNS(213.136.95.10)가 불안정 → 외부 API 전부 fetch failed

**Why:** Discord WebSocket + Anthropic API 동시 연결 불가

**How to apply:**
- `/etc/systemd/resolved.conf.d/dns.conf`에 Google(8.8.8.8) + Cloudflare(1.1.1.1) DNS 설정
- Contabo DNS는 fallback으로만 사용

## 4. systemd 서비스 파일 보호
에이전트가 자기 서비스 파일을 삭제함 (oracle)

**Why:** ORACLE 서비스 파일이 삭제되어 재시작 불가

**How to apply:**
- `chattr +i`로 서비스 파일 immutable 설정
- SOUL.md에 systemd 파일 수정/삭제 금지 명시

## 5. 에이전트 순차 재시작
3개를 동시에 재시작하면 Discord gateway 경쟁으로 전부 연결 실패

**How to apply:**
- 재시작 시 15~20초 간격으로 순차 시작
