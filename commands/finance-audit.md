# nexus-finance-mcp 종합 감사

nexus-finance-mcp 서버 전체 상태를 점검해.

## 체크리스트

1. **서비스 상태**: `systemctl status nexus-finance-mcp` + `curl http://127.0.0.1:8100/health`
2. **서버/도구 수**: 27서버, 131도구, 0실패 확인
3. **프로세스 유저**: mcpserver로 실행 중인지 (`ps -o user -p $(pgrep -f "server.py.*8100")`)
4. **HTTPS**: `curl -sk https://127.0.0.1/api/mcp/health` 정상 응답 확인
5. **공개 MCP**: `curl -s http://62.171.141.206/mcp -X POST -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"check","version":"1"}}}'` 정상 응답
6. **에러 로그**: `journalctl -u nexus-finance-mcp --since "1 hour ago" | grep -iE "error|fail|traceback"` 확인
7. **nginx**: `nginx -t` 문법 확인
8. **mcporter**: `mcporter call nexus-finance.gateway_status` 호출 테스트

결과를 요약 테이블로 보여줘.
