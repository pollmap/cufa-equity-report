---
name: MCP 도구 우선 사용
description: 데이터 수집 시 MCP 도구를 웹 스크래핑보다 먼저 사용
type: feedback
---

MCP 도구가 있으면 항상 MCP 먼저 사용, 웹 스크래핑은 fallback.

**Why:** Insights 분석(2026.03.28) 결과, 여러 세션에서 찬희가 MCP 사용을 지시했는데 Claude가 웹 스크래핑부터 시작해서 수정 지시를 반복해야 했음. 특히 Nexus MCP 126도구가 있는데 무시하고 스크래핑하는 패턴.

**How to apply:**
- 데이터 수집 작업 시 먼저 사용 가능한 MCP 도구 목록 확인
- Nexus Finance MCP가 커버하는 영역(주식, 거시경제, 암호화폐, 뉴스 등)은 무조건 MCP 우선
- MCP로 데이터를 못 구할 때만 웹 스크래핑/WebFetch 사용
