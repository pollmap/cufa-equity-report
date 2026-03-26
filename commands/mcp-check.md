# MCP 서버 헬스체크

MCP 서버 상태와 도구 수를 빠르게 확인해.

## 실행

1. `systemctl status nexus-finance-mcp --no-pager | head -10`
2. 도구 수 확인:
```bash
cd /root/nexus-finance-mcp && python3 -c "
import asyncio
from mcp_servers.gateway.gateway_server import GatewayServer
async def main():
    g = GatewayServer()
    tools = await g.mcp.list_tools()
    print(f'Total: {len(tools)}')
    vault = [t.name for t in tools if 'vault' in t.name]
    print(f'Vault ({len(vault)}): {vault}')
asyncio.run(main())
" 2>/dev/null
```
3. 포트 확인: `ss -tlnp | grep 8100`

기대값: 126개 도구, vault 6개. 다르면 경고.
