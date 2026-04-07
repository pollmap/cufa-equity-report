---
name: sidebar_wrap 안에 차트/테이블 절대 금지
description: sidebar_wrap 내부에는 텍스트(p/strong/u)만, SVG/table/counter_arg는 반드시 밖에
type: feedback
---

sidebar_wrap(kws, content) 안에 차트, 테이블, counter_arg 블록을 절대 넣지 않는다.

**Why:** sidebar-layout은 grid-template-columns: 180px 1fr 구조인데, SVG/table이 1fr 칼럼에 들어가면 max-width를 넘어서 사이드바 영역을 밀어내고, 이후 모든 레이아웃이 깨진다. 찬희님이 "절대로 사이드바 침범하지마"라고 반복 지시.

**How to apply:**
- sidebar_wrap 안: `<p>`, `<strong>`, `<u>`, `<br>` 텍스트만
- sidebar_wrap 밖: chart_with_context, chart-pair, table, counter_arg, callout, insight_box, expand_card
- 서브에이전트 프롬프트에도 반드시 명시
- CSS 안전장치: `.sidebar-body svg { display: none; }` (실수 방지)
