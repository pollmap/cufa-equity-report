# /svc-verify — 서비스 검증 (restart 후)

서비스 재시작 후 정상 동작 여부만 검증. restart는 하지 않음.

## 사용법
```
/svc-verify [서비스명]
```
서비스명: `mcp` | `hermes` | `nexus` | `oracle` | `adapter` | `avatar` | `nginx` | `all`

## 서비스 매핑

| 서비스명 | systemd | 포트 | health URL |
|---------|---------|------|-----------|
| mcp | nexus-finance-mcp | 8100 | http://127.0.0.1:8100/health |
| luxon-mcp | luxon-mcp-http | 8000 | http://127.0.0.1:8000/health |
| hermes | openclaw-hermes | 18789 | - |
| nexus | openclaw-nexus | 18790 | - |
| oracle | openclaw-oracle | 18800 | - |
| adapter | luxon-adapter | 11434 | http://127.0.0.1:11434/health |
| avatar | luxon-avatar | 12393 | - |
| nginx | nginx | 80 | http://localhost/health |

## 검증 순서

### 1. 서비스 활성 상태
```bash
systemctl is-active [systemd유닛]
```

### 2. 포트 리스닝
```bash
ss -tlnp | grep :[포트]
```

### 3. Health 엔드포인트 (해당 서비스만)
```bash
curl -sf --max-time 3 http://127.0.0.1:[포트]/health
```

### 4. 최근 로그 (에러 확인)
```bash
journalctl -u [systemd유닛] --no-pager -n 10 --since "2 min ago" | grep -i -E "error|fail|crash" || echo "no errors"
```

### 5. MCP 전용 추가 (mcp일 때)
```bash
curl -s http://127.0.0.1:8100/health | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Tools: {d[\"tool_count\"]}, Servers: {d[\"loaded_servers\"]}, Failed: {d[\"failed_servers\"]}')
"
```

## 출력 형식

```
[VERIFY] nexus-finance-mcp
  Service:  active
  Port:     127.0.0.1:8100 LISTENING
  Health:   200 OK (131 tools, 27 servers, 0 failed)
  Errors:   none in last 2 min
  Result:   PASS
```
