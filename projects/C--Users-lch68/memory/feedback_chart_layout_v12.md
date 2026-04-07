---
name: 도표 배치 규칙 (v12 실전 교훈)
description: 차트는 파트 마지막, 반드시 2개씩 pair, 본문 중간 삽입 절대 금지
type: feedback
---

도표/시각화 배치 절대 규칙 (2026.03.28 플리토 보고서 실전 교훈):

1. **텍스트 먼저, 차트는 파트(h3/h4) 마지막에만**
   - 각 소제목 블록 안에서: sidebar_wrap(텍스트) 전부 → 마지막에 차트+테이블 모아서
   - 본문 중간에 차트 끼워넣기 절대 금지

2. **차트는 반드시 2개씩 chart-pair로 묶기**
   - 단독 chart-box 금지 → 항상 `<div class="chart-pair">` 안에 2개씩
   - 홀수면 마지막 1개만 단독 허용
   - 서브에이전트가 코드 작성할 때부터 chart-pair로 묶어서 생성

3. **chart-box max-width: 480px** (컨테이너 절반)
   - chart-pair 안에서는 max-width 해제 (각각 50% 차지)

**Why:** 서브에이전트가 chart_with_context(pre, chart, post) 패턴으로 작성하면 필연적으로 차트가 텍스트 사이에 끼게 된다. chart_with_context 패턴 자체를 폐기하고, 텍스트 블록과 차트 블록을 완전 분리해야 한다.

**How to apply:**
- chart_with_context() 함수 사용 금지 → 대신 텍스트는 sidebar_wrap, 차트는 chart-pair로 분리
- 서브에이전트 프롬프트에 "chart_with_context 사용 금지, 텍스트와 차트 완전 분리" 명시
- build 후처리로 auto_pair_charts 적용 (라인 기반)
