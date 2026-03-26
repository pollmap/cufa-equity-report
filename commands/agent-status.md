# 에이전트 전체 상태 확인

VPS 3개 + WSL 3개, 총 6개 에이전트 상태를 확인해.

## VPS 에이전트
각 에이전트 포트로 curl 체크:
- HERMES: `curl -sf http://localhost:18789/health 2>/dev/null || curl -sf http://localhost:18789/ 2>/dev/null | head -1`
- NEXUS: `curl -sf http://localhost:18790/health 2>/dev/null || curl -sf http://localhost:18790/ 2>/dev/null | head -1`
- ORACLE: `curl -sf http://localhost:18800/health 2>/dev/null || curl -sf http://localhost:18800/ 2>/dev/null | head -1`

## WSL 에이전트
SSH로 확인:
```bash
ssh -o ConnectTimeout=5 valuealpha@10.0.0.2 "
echo '=== CHIEF ==='; systemctl --user status openclaw-chief 2>/dev/null | head -3 || echo 'not systemd'
echo '=== DOGE ==='; systemctl --user status openclaw-doge 2>/dev/null | head -3 || echo 'not systemd'
echo '=== GATE ==='; ls ~/gate-home/ 2>/dev/null && echo 'exists' || echo 'workspace not created'
"
```

## 출력
| 에이전트 | 위치 | 포트 | 상태 |
