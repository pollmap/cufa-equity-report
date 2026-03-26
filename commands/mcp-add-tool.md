# /mcp-add-tool — MCP 도구 추가 워크플로우

nexus-finance-mcp에 새 도구 또는 서버를 추가하는 표준 절차.

## 사용법
```
/mcp-add-tool [도구명 또는 서버 설명]
```

## 새 도구 추가 (기존 서버에)

### 1. 대상 서버 파일 확인
```
/root/nexus-finance-mcp/mcp_servers/servers/[서버]_server.py
```

### 2. 도구 등록 패턴
기존 패턴 따라 `_register_tools()` 안에 추가:
```python
@self.mcp.tool()
def 도구명(param1: str, param2: int = 10) -> dict:
    """
    도구 설명 (한국어)

    Args:
        param1: 파라미터 설명
        param2: 기본값 설명
    """
    try:
        # 구현
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"도구명 error: {e}")
        return {"error": True, "message": "처리 중 오류 발생"}
```

### 3. 캐시/레이트리밋 활용
```python
# 캐시 사용
result = self._cache.get("namespace", cache_key)
if result:
    return result
# ... fetch ...
self._cache.set("namespace", cache_key, result, "daily_data")

# 레이트리밋
self._limiter.acquire("service_name")
```

## 새 서버 추가

### 1. 서버 파일 생성
```
/root/nexus-finance-mcp/mcp_servers/servers/[이름]_server.py
```

BaseMCPServer 또는 직접 FastMCP 패턴:
```python
from fastmcp import FastMCP

class NewServer:
    def __init__(self):
        self.mcp = FastMCP("서버이름")
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        def tool_name(...) -> dict:
            ...
```

### 2. 게이트웨이에 등록
`/root/nexus-finance-mcp/mcp_servers/gateway/gateway_server.py`의 SERVERS 리스트에 추가:
```python
("key", "mcp_servers.servers.new_server", "NewServer"),
```

### 3. 어댑터 필요 시
```
/root/nexus-finance-mcp/mcp_servers/adapters/[이름]_adapter.py
```
외부 API 래퍼 생성. 캐시/레이트리밋/에러핸들링 포함.

### 4. 의존성
`requirements.txt`에 추가 후:
```bash
pip3 install --break-system-packages -r requirements.txt
```

### 5. 배포
```
/deploy mcp
```

### 6. 검증
```bash
curl -s http://127.0.0.1:8100/health | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'Tools: {d[\"tool_count\"]}, Servers: {d[\"loaded_servers\"]}, Failed: {d[\"failed_servers\"]}')
"
```
- tool_count 증가 확인
- failed_servers = 0 확인

## 체크리스트
- [ ] 도구 이름에 서버 prefix 포함 (예: `ecos_`, `vault_`, `viz_`)
- [ ] Args 독스트링 한국어로 작성
- [ ] 에러 반환 형식: `{"error": True, "message": "..."}`
- [ ] 성공 반환 형식: `{"success": True, "data": ...}`
- [ ] 캐시 TTL 적절 (realtime: 60s, daily: 3600s, historical: 86400s)
- [ ] 레이트리밋 적용 (외부 API 호출 시)
- [ ] 에러 메시지에 내부 경로/스택 미포함
