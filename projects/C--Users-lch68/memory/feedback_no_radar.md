---
name: 레이더 차트 절대 금지
description: svg_radar 함수 사용 금지, 모든 보고서에서 레이더/스파이더 차트 제거
type: feedback
---

레이더 차트(svg_radar, 스파이더 차트) 절대 사용 금지.

**Why:** 정성적 점수(경영진 역량 4점 등)로 축을 채우면 근거 없는 분석이 되고, 정량 데이터로 채워도 축 간 스케일이 달라 왜곡된다. 찬희님이 "아예 없애라"고 명시적으로 지시.

**How to apply:** svg_radar 함수 호출 0건. Peer 비교는 바 차트/테이블/산점도로 대체. build_template.py에서 함수 자체를 삭제하거나 호출 시 에러를 raise.
