---
name: 플리토(300080) CUFA 보고서
description: 플리토 CUFA 기업분석보고서 v12 스킬, Phase 4 빌드 완료 but 레이아웃 재빌드 필요
type: project
---

2026.03.28 플리토(300080) CUFA 보고서.

**현재 상태:** Phase 4 v4 빌드 완료 (67K자/52SVG/42T) but 레이아웃 문제로 **처음부터 재빌드** 필요.

**Why:** 서브에이전트 패치 방식으로 도표 배치 수정 시도했으나 실패. 본문 중간에 차트가 끼는 구조적 문제.

**재빌드 시 적용할 규칙 (이번 세션 교훈):**
1. chart_with_context() 폐기 → 텍스트/차트 완전 분리
2. 차트는 각 파트(h3/h4) 마지막에만, 반드시 2개씩 chart-pair
3. sidebar_wrap 안에는 텍스트만 (SVG/table/counter_arg 밖에)
4. 레이더 차트 절대 금지
5. 주가 구간별 분석 절대 금지
6. CSS 압축: 12.5px/1.6, max-width 1000px
7. Appendix = 테이블만 (텍스트 설명 최소화)
8. 커버: 좌=IP(5~6줄 SMIC)+IS, 우=투자의견+Metrics
9. 이미지: Wikipedia 로고 URL 확보 완료

**확보된 이미지 URL:**
- 로고: `https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flitto_sns_profile.png/250px-Flitto_sns_profile.png`
- Google Cloud 사례: `https://lh3.googleusercontent.com/ov4h2udwCQBGfV0TVarw-eOXKR5-8s5a9S2lcRu4co80c7cTHweKNUG9pmFuoJHu1F4Me3LZ3bkIzGTxkmFRWzvQD6I9esOeaWgBzQ`

**프로젝트 위치:** `~/Desktop/cufa_report_300080/`
- sections/config.py — 종목 데이터 (완성, 재사용)
- phase0_dart_data.json — DART 재무 (완성, 재사용)
- phase0_stock_macro.json — 주가/매크로 (완성, 재사용)
- build_flitto.py — 헬퍼 함수 (CSS 수정 완료, 재사용)

**투자포인트 3개 (확정):**
① "AI가 먹는 데이터, 동사가 키운다" — 빅테크 데이터 공급자
② "적자의 끝, 흑자의 시작" — 구조적 BEP 돌파
③ "ATH -80%, 시장이 놓친 것" — 밸류에이션 디스커넥트

**다음 세션:** 프롬프트 파일 준비됨 → /cufa-equity-report 호출 → 재빌드
