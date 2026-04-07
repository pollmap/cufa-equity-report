---
name: Nexus Finance MCP 실전 리포트
description: KSS해운 Phase 0에서 발견한 MCP 19개 이슈 (P0 버그 3, P1 누락 5, P2 부족 5, P3 확장 6)
type: reference
---

Vault 위치: `02-Areas/mcp-improvement/nexus-finance-mcp-field-report-2026-03-28.md`

핵심 P0 이슈:
- stocks_beta 크래시 ('지수명' KeyError)
- maritime 3개 도구 전부 빈 데이터
- ECOS JSON 키 한국어 인코딩 깨짐

핵심 P1 누락:
- DART CF(현금흐름표), 세부계정, 사업보고서 본문
- 국고채 금리, stocks_history interval 옵션
