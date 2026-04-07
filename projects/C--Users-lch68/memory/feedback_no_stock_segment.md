---
name: 주가 구간별 분석 금지
description: gen_stock_analysis() 같은 AI 자체 주가 메타분석 섹션 금지
type: feedback
---

주가 구간별 분석(gen_stock_analysis) 절대 하지 않는다.

**Why:** AI가 스스로 생성한 보고서의 주가를 다시 분석하는 건 메타적으로 이상하다. 주가 데이터는 표지 Key Charts에 소형 차트로만 포함하고, 별도 "주가분석" 섹션은 만들지 않는다.

**How to apply:** gen_stock_analysis() 함수 삭제. 주가 차트는 표지 또는 Key Charts의 4개 중 1개로만 포함. SKILL.md 섹션 31-8의 "주가분석 섹션 금지" 규칙을 엄격히 따를 것.
