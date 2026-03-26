# Luxon 인프라 전체 감사

전체 인프라 상태를 점검하고 결과를 테이블로 보고해.

## 체크리스트 (순서대로 실행)

### 1. 서비스 상태
- `systemctl status nexus-finance-mcp luxon-mcp-http nginx` + 3개 VPS 에이전트 (HERMES :18789, NEXUS :18790, ORACLE :18800)
- 각각 active/inactive 표시

### 2. MCP 도구 수 확인
```bash
cd /root/nexus-finance-mcp && python3 -c "
import asyncio
from mcp_servers.gateway.gateway_server import GatewayServer
async def main():
    g = GatewayServer()
    tools = await g.mcp.list_tools()
    print(f'Total: {len(tools)}')
    vault = [t.name for t in tools if 'vault' in t.name]
    print(f'Vault: {vault}')
asyncio.run(main())
" 2>/dev/null
```

### 3. 크론 점검
- `crontab -l` 로 크론 목록 확인, 각각 정상 여부

### 4. 데이터 파일 유효성
- `/root/nexus-finance-mcp/data/*.json` 모두 `python3 -m json.tool` 로 검증

### 5. 파일 권한
- `.env`, credentials, config 파일들이 600 권한인지 확인
- `/root/nexus-finance-mcp/.env`, `/root/luxon-mcp/.env` 등

### 6. Vault 상태
- `/root/obsidian-vault/` — git status, 노트 수, 최근 커밋

### 7. WSL 연결
- `ssh -o ConnectTimeout=5 valuealpha@10.0.0.2 echo OK`

### 8. Nginx
- `nginx -t`

### 9. 대시보드
- `curl -sf http://localhost/ | head -5`

## 출력 형식
결과를 마크다운 테이블로 정리:
| 항목 | 결과 | 비고 |
