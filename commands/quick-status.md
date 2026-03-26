# /quick-status — 빠른 상태 확인

세션 시작 시 5초 내 핵심 인프라 상태만 확인. `/audit`의 경량 버전.

## 실행 방법

### 1. 서비스 상태 (한줄 체크)
```bash
for svc in openclaw-hermes openclaw-nexus openclaw-oracle nexus-finance-mcp luxon-mcp-http luxon-kakao luxon-adapter luxon-avatar luxon-feed strategy-engine nginx; do
  status=$(systemctl is-active $svc 2>/dev/null)
  echo "$svc: $status"
done
```

### 2. 핵심 포트 + health
```bash
for entry in "8100:MCP" "18789:HERMES" "18790:NEXUS" "18800:ORACLE" "80:nginx"; do
  port=${entry%%:*}; name=${entry##*:}
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:$port/health 2>/dev/null)
  echo "$name(:$port): $code"
done
```

### 3. MCP 도구 수
```bash
curl -s http://127.0.0.1:8100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Tools: {d[\"tool_count\"]}, Servers: {d[\"loaded_servers\"]}, Failed: {d[\"failed_servers\"]}')" 2>/dev/null
```

### 4. 리소스
```bash
echo "Disk: $(df -h / | awk 'NR==2{print $5, $4\" free\"}')"
echo "Mem: $(free -h | awk 'NR==2{printf "%s/%s (%.0f%%)", $3, $2, $3/$2*100}')"
```

## 출력 형식

마크다운 테이블 1개로 정리:
| 서비스 | 상태 | 포트 | 비고 |
