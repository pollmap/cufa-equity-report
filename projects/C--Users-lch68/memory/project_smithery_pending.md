---
name: Smithery 등록 보류
description: nexus-finance-mcp Smithery 등록 — Apify Standby URL 받은 후 진행
type: project
---

nexus-finance-mcp Smithery 등록 보류 중.

**Why:** Smithery는 public HTTPS URL 필요. VPS에 도메인/SSL 없음.
**How to apply:** Apify Actor(fdEXWOxIXx9Cb2shh) Standby 모드 활성화 후 받는 HTTPS URL로 Smithery에 등록. 또는 도메인+SSL 설정 후 직접 등록.

**Smithery 등록 방법:**
1. https://smithery.ai/new 접속 (GitHub 로그인)
2. Apify Standby URL 입력 (HTTPS)
3. 또는 CLI: `smithery mcp publish "https://..." -n @pollmap/nexus-finance-mcp`
