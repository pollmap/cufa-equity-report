---
name: CUFA 보고서 산출물 일관성 규칙
description: 매번 CSS를 새로 만들지 말고 HD건설기계 v4-1의 검증된 CSS/구조를 표준으로 확정. 땜빵 금지.
type: feedback
---

CUFA 보고서는 **검증된 CSS를 재사용**해야 하며, 매번 새로 만들면 안 된다.

**Why:** 이노스페이스 보고서 빌드 과정에서 build_template.py를 처음부터 새로 만들었더니 HD건설기계 v4-1보다 품질이 낮았다. CSS 수정을 7번 반복(v1→v7)하면서 땜빵만 했고 결과는 일관되지 않았다.

**How to apply:**
1. **HD건설기계 v4-1의 CSS = 표준.** 새 보고서 빌드 시 이 CSS를 그대로 복사하고, 데이터만 교체.
2. **build_template.py의 CSS를 절대 새로 작성하지 않는다.** hd_style.css를 표준으로 embed.
3. **HTML 클래스명 통일:** .report, .cover, .cover-main, .cover-sidebar, .section, .section-header, .section-num, .section-title, .sidebar-layout, .sidebar-kw, .content-area, .chart-pair, .chart-box, .metric-grid, .scenario-grid, .risk-grid, .footer — 이 클래스만 사용.
4. **새 컴포넌트 추가 시:** 기존 CSS에 추가하되 기존 스타일 수정 금지.
5. **에이전트에게 CSS 생성 요청 금지.** CSS는 항상 표준 파일에서 복사.
