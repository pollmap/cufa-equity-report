"""CUFA Builder — 디자인 토큰.

단일 표준. 수정 금지. 새 색상·radius 필요 시 PR + CHANGELOG 근거 첨부.
SKILL.md §1.5 구현체.
"""
from __future__ import annotations

from typing import Final


#: 전체 CSS 변수. `gen_css()`는 이 dict를 직접 읽지 않고 문자열로 하드코딩하지만,
#: Python 레벨에서 색상을 인용해야 할 때 (SVG 기본값 등) 이 dict를 단일 출처로 사용한다.
CSS_VARS: Final[dict[str, str]] = {
    "bg": "#0a0a0a",
    "surface": "#111111",
    "surface2": "#1a1a1a",
    "border": "#2a2a2a",
    "border2": "#3a3a3a",
    "purple": "#7c6af7",
    "purple_light": "#a78bfa",
    "purple_bg": "#12101f",
    "purple_border": "#2d2654",
    "blue": "#6cb4ee",
    "positive": "#4ecdc4",
    "negative": "#ff6b6b",
    "amber": "#ffd93d",
    "text": "#e0e0e0",
    "text_sec": "#888888",
    "text_tert": "#555555",
}


#: 역할 기반 차트 색상. SVG 함수에서 `color=CHART_COLOR_ROLES["actual"]` 식으로 사용.
CHART_COLOR_ROLES: Final[dict[str, str]] = {
    "actual": CSS_VARS["purple"],
    "estimate": CSS_VARS["purple_light"],
    "peer": CSS_VARS["blue"],
    "positive": CSS_VARS["positive"],
    "negative": CSS_VARS["negative"],
    "warning": CSS_VARS["amber"],
    "gray": CSS_VARS["text_tert"],
}


#: 전역 border-radius (px). 8px 등 임의 변경 금지 — 디자인 일관성 훼손.
BORDER_RADIUS: Final[int] = 2


#: 폰트 스택. Google Fonts Noto Sans KR 우선, fallback 맑은 고딕.
FONT_FAMILY: Final[str] = "'Noto Sans KR', '맑은 고딕', 'Malgun Gothic', sans-serif"


#: Peer/기업 비교 시 기본 팔레트. 5개 이상 필요하면 추가 대신 그룹화 권장.
DEFAULT_PALETTE: Final[tuple[str, ...]] = (
    CSS_VARS["purple"],
    CSS_VARS["purple_light"],
    CSS_VARS["positive"],
    CSS_VARS["blue"],
    CSS_VARS["amber"],
)
