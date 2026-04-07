---
name: CSS 간격/폰트 압축 규칙
description: 글자 12.5px, 간격 1.6, 여백 최소화, 보고서 밀도 최대화
type: feedback
---

HTML 보고서 CSS 압축 규칙 (찬희님 직접 피드백):

- body: 12.5px, line-height 1.6 (14px/1.8은 너무 크다)
- h2: 18px, h3: 14px, h4: 13px
- section margin: 28px, padding: 24px
- sidebar-layout gap: 14px, sidebar width: 150px
- chart-box padding: 10px, margin: 10px
- table font: 11.5px, th padding: 7px 8px, td padding: 5px 8px
- cover h1: 28px (36px 너무 크다)
- report-wrap max-width: 1000px (1100px 너무 넓다)
- page-break height: 40px, margin: 28px

**Why:** "글자나 전체 간격들이 종합적으로 다 크고 넓다" — 찬희님 원문

**How to apply:** 모든 보고서 빌드 시 위 수치 적용. SKILL.md의 CSS 변수 섹션도 업데이트 필요.
