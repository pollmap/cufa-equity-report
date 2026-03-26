# MCP 서버 재시작

nexus-finance-mcp 서버를 재시작하고 정상 동작을 확인해.

## 실행

1. `systemctl restart nexus-finance-mcp`
2. `sleep 3`
3. `systemctl status nexus-finance-mcp --no-pager | head -10`
4. 도구 수 확인:
```bash
cd /root/nexus-finance-mcp && python3 -c "
import asyncio
from mcp_servers.gateway.gateway_server import GatewayServer
async def main():
    g = GatewayServer()
    tools = await g.mcp.list_tools()
    print(f'Total: {len(tools)}')
asyncio.run(main())
" 2>/dev/null
```

기대값: active + 126개 도구. 실패 시 `journalctl -u nexus-finance-mcp --no-pager -n 30` 로 로그 확인.
