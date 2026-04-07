---
name: feedback_competition_workflow
description: 공모전/경시대회 작업 시 프리셋 선택→검증→시각화→빌드 파이프라인 + 크로스스킬 오케스트레이션
type: feedback
---

공모전/경시대회 작업 요청 시 competition-arsenal 스킬의 프리셋 워크플로우를 따를 것.

**Why:** 전세 토론 시각자료 세션에서 데이터 검증, 출처 표기, 멀티포맷 산출물 필요성이 확인됨. 찬희님이 한국은행 경시대회, DB IFC, 리서치 아카데미아 등 다수 금융권 대회에 참가하며, 대회마다 요구 형식이 다름 (토론=PNG+대본, 리서치=DOCX+XLSX, 아이디어=PPTX+HTML).

**How to apply:**
1. 공모전 관련 요청 시 먼저 프리셋 확인 (debate/research/idea/data/paper/public-data)
2. 프리셋에 따라 연계 스킬 자동 호출 (bok-report-writing, pptx, mla-dsa-analysis 등)
3. nexus-finance MCP 126도구를 카테고리별로 활용 (거시/부동산/주식/DART/뉴스/학술)
4. Karpathy AutoResearch 패턴: 병렬 에이전트 검증, 반복 개선 루프
5. KIC 논문 등 AI 사용 금지 대회 주의
