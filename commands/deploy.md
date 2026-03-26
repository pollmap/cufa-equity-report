# /deploy — 서비스 배포 (편집→재시작→검증)

코드 변경 후 서비스 안전 배포. 재시작 전후 상태 비교.

## 사용법
```
/deploy [서비스명]
```
서비스명: `mcp` | `luxon-mcp` | `hermes` | `nexus` | `oracle` | `adapter` | `avatar` | `nginx` | `all`

## 배포 순서

### 1. Pre-deploy 상태 스냅샷
```bash
# 현재 서비스 상태 기록
systemctl is-active [서비스]
ss -tlnp | grep [포트]
curl -s http://127.0.0.1:[포트]/health
```

### 2. 서비스 매핑

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

### 3. 재시작
```bash
systemctl restart [서비스명]
sleep 5  # MCP는 20초 (26서버 로딩)
```

### 4. Post-deploy 검증
```bash
systemctl is-active [서비스]
ss -tlnp | grep [포트]
curl -s http://127.0.0.1:[포트]/health
journalctl -u [서비스] --no-pager -n 20 --since "2 min ago"
```

### 5. MCP 전용 추가 검증 (mcp 배포 시)
```bash
# 도구 수 확인 (126개 기대)
curl -s http://127.0.0.1:8100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Tools: {d[\"tool_count\"]}, Servers: {d[\"loaded_servers\"]}, Failed: {d[\"failed_servers\"]}')"
```

### 6. nginx 전용 (nginx 배포 시)
```bash
nginx -t && systemctl reload nginx
```

## 출력 형식

```
[DEPLOY] nexus-finance-mcp
  Pre:  active | 127.0.0.1:8100 | health OK
  Action: systemctl restart nexus-finance-mcp
  Post: active | 127.0.0.1:8100 | health OK (126 tools, 26 servers)
  Result: SUCCESS
```

## 롤백
실패 시 이전 코드로 git checkout + 재시작:
```bash
cd /root/nexus-finance-mcp && git diff  # 변경 확인
git checkout -- [파일]                   # 롤백
systemctl restart [서비스]               # 재시작
```
