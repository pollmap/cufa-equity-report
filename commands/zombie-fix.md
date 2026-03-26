---
description: "OpenClaw 에이전트 좀비 gateway 수정 — 포트 충돌로 restart 루프 빠졌을 때"
---

# Zombie Gateway Fix

OpenClaw 에이전트가 포트 충돌로 restart 루프에 빠졌을 때 사용.
원인: systemctl restart 시 이전 gateway 프로세스가 안 죽고 포트 점유.

## 절차

1. 대상 에이전트 확인 (HERMES:18789, NEXUS:18790, ORACLE:18800)
2. 서비스 중지: `systemctl stop openclaw-{agent}`
3. 포트 점유 프로세스 확인: `ss -tlnp | grep {port}`
4. 좀비 gateway kill: `fuser -k {port}/tcp`
5. 포트 해제 확인: `ss -tlnp | grep {port}` → 결과 없어야 함
6. 서비스 시작: `systemctl start openclaw-{agent}`
7. 15초 후 안정성 확인: `systemctl is-active openclaw-{agent}`

## 주의
- NEXUS는 `Restart=no` + `RemainAfterExit=yes` 설정 (gateway fork 구조)
- HERMES/ORACLE은 `Restart=always` (메인 프로세스 살아있음)
- `kill -9`은 마지막 수단으로만 사용

$ARGUMENTS 가 있으면 해당 에이전트에 대해 자동 실행.
없으면 3개 에이전트 모두 상태 확인 후 문제 있는 것만 수정.
