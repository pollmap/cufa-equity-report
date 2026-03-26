# /log-check — 전체 서비스 에러 로그 스캔

모든 서비스의 최근 에러/경고 로그를 수집하고 패턴 분석.

## 실행 순서

### 1. systemd 서비스 로그 (최근 1시간)
```bash
# VPS 에이전트
journalctl -u openclaw-hermes --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10
journalctl -u openclaw-nexus --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10
journalctl -u openclaw-oracle --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10

# MCP 서버
journalctl -u nexus-finance-mcp --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10
journalctl -u luxon-mcp-http --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10

# 어댑터/아바타
journalctl -u luxon-adapter --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10
journalctl -u luxon-avatar --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10

# nginx
journalctl -u nginx --no-pager --since "1 hour ago" -p err 2>/dev/null | tail -10
```

### 2. 애플리케이션 로그
```bash
# MCP 서버 nohup 로그
tail -50 /root/nexus-finance-mcp/nohup.out 2>/dev/null | grep -i -E '(error|exception|traceback|fail)'

# nginx 에러 로그
tail -30 /var/log/nginx/error.log 2>/dev/null
```

### 3. 크론 로그
```bash
# MCP 캐시
tail -20 /root/scripts/mcp-cache.log 2>/dev/null | grep -E '(ERR|FAIL)'

# Vault 동기화
tail -20 /root/obsidian-vault/scripts/sync.log 2>/dev/null | grep -i error

# 대시보드 데이터
tail -10 /root/scripts/dashboard-data.log 2>/dev/null | grep -i error
```

### 4. Vault git push 상태
```bash
cat /root/obsidian-vault/.git-push-status 2>/dev/null || echo "OK (no failures)"
```

### 5. 서비스 재시작 횟수 (비정상 종료 감지)
```bash
for svc in openclaw-hermes openclaw-nexus openclaw-oracle nexus-finance-mcp luxon-mcp-http; do
  restarts=$(systemctl show $svc --property=NRestarts 2>/dev/null | cut -d= -f2)
  echo "$svc: $restarts restarts"
done
```

## 출력 형식

| 서비스 | 에러 수 | 최근 에러 | 재시작 횟수 |
|--------|---------|----------|------------|
| hermes | 0 | - | 0 |
| nexus | 2 | ClosedResourceError | 1 |
| ... | ... | ... | ... |

### 에러 패턴 분석
반복되는 에러는 근본 원인과 수정 방안 함께 제시:
- `ClosedResourceError` → SSE 클라이언트 disconnect (streamable-http 전환으로 해결)
- `TimeoutError` → 외부 API 응답 지연 (타임아웃 조정 또는 캐시 활용)
- `ImportError` → 패키지 미설치 (pip install)
