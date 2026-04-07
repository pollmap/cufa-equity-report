---
name: NEXUS 디스코드 중복 응답 — 해결 완료
description: 디스코드 2번 답변 + session lock 반복의 근본 원인과 해결 기록
type: project
---

## 해결 완료 (2026-03-28)

### 근본 원인
OpenClaw이 자동 생성한 **user-level systemd 서비스** (`~/.config/systemd/user/openclaw-gateway.service`)가 같은 NEXUS Discord 봇 토큰으로 포트 18788에서 동시 접속. system-level 서비스(18790)와 합쳐서 Discord 메시지가 2번 처리됨. session lock 반복도 2개 gateway가 같은 세션 파일을 동시에 잠그면서 발생.

### 적용한 수정
1. `systemctl --user stop/disable openclaw-gateway.service` — 재부팅해도 안 올라옴
2. 3개 서비스 파일에서 `RemainAfterExit=yes` 제거 (좀비 프로세스 방지)
3. `/root/clear_stale_locks.sh` → ExecStartPre에 등록 (재시작 시 stale lock 자동 정리)

### 주의사항
- `openclaw` CLI가 `openclaw gateway install` 등으로 user-level 서비스를 다시 만들 수 있음 → 주기적 확인 필요
- `pkill -f openclaw`은 다른 에이전트까지 죽이므로 절대 금지. 포트별 `fuser -k`만 사용
