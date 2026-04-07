---
name: JYP 보고서 v2 수정 계획
description: JYP v1 SMIC 48점 → v2 85점+ 목표, 핵심 수정 16건 정리 (2026.03.28)
type: project
---

JYP v1 빌드 완료 (375KB, 79K자, SVG 65, HARD_MIN 10/10) but SMIC 대비 48점.
다크 전용 확정, 화이트 토글 삭제 완료.

**Why:** 서브에이전트에 스킬 v10/v11 규칙 미전달 → 차트 깨짐, 이미지 없음, chart-pair 부족

**How to apply — v2 수정 16건:**

### CSS/Template (build_template.py)
1. ✅ 다크 전용 (화이트 제거 완료)
2. ✅ chart-box 배경 var(--chart-bg) (완료)
3. ⬜ SVG 헬퍼 내부: rect fill 투명/다크 강제
4. ⬜ 섹션 카드 스타일 강화 (page-like 느낌)

### 섹션 파일 수정 (5개 병렬 에이전트)
5. ⬜ chart-pair 8→17+ (모든 병렬 가능 차트 pair로)
6. ⬜ 빈 차트/비례 깨짐 수정 (auto_base, 데이터 검증)
7. ⬜ 레이더 자체평가 제거 → Peer 정량 비교만
8. ⬜ sidebar_wrap 안에 차트 있으면 밖으로 이동
9. ⬜ 이미지 추가 (JYP 홈페이지 아티스트 사진 2-3장)

### 콘텐츠 품질
10. ⬜ OPM 하락 원인 분석 강화 (핵심 VP)
11. ⬜ 주가 조정 이유 상세 (136,400→64,300 구간 분석)
12. ⬜ Appendix 테이블 16개 확인
13. ⬜ counter_arg 각 IP 본문 내 통합

### 엑셀/산출물
14. ⬜ build_excel_v2.py JYP용 생성
15. ⬜ 엑셀 15시트 빌드
16. ⬜ 최종 빌드 + HARD_MIN + SMIC 채점 85점+

### 서브에이전트 프롬프트 개선 핵심 (스킬 29-8):
```
□ 다크 전용: 모든 색상 var() 변수만. #ffffff, #fef2f2 등 하드코딩 절대 금지
□ chart-pair 60%: 관련 차트 2개는 반드시 pair
□ sidebar_wrap 안에 차트 금지: 텍스트만 wrap, 차트는 밖
□ add_source → chart_with_context 순서
□ svg_radar: Peer 정량 비교만. 자체평가 금지
□ 이미지: config.py IMAGES dict에서 URL 가져오기
□ auto_base=True: 값 차이 작은 bar 차트
□ counter_arg: IP마다 1건 본문 내 통합
```
