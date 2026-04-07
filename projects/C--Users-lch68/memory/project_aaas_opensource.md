---
name: AaaS 오픈소스 배포 계획
description: 퀀트 시스템(MCP+파이프라인+CUFA)을 AaaS로 오픈소스 배포, 공공성/실용성/진실성 핵심 가치
type: project
---

# AaaS (Agent/Analysis as a Service) 오픈소스 계획

2026.04.05 찬희 확정:
- Nexus MCP 364도구 + 퀀트 파이프라인 + CUFA 보고서를 **오픈소스로 배포**
- 핵심 가치: **공공성, 실용성, 진실성, 합리성, 사랑**
- 개인투자자가 헤지펀드급 분석 인프라를 무료로 쓸 수 있게
- CUFA 할루시네이션 금지 원칙 = 진실성의 코드화

**Why:** 찬희의 근본 철학 — 도구는 공유될 때 가치가 극대화. 수익은 SaaS 프리미엄/컨설팅으로.
**How to apply:** 
- 모든 코드에서 하드코딩 제거 (env var, config)
- 다른 사용자가 자기 MCP 서버/API 키로 바로 실행 가능하게
- README, 설치 가이드, .env.example 필수
- 오픈소스 전 보안 스캔 (API 키, 토큰 노출 방지)
