"""CUFA Sections — 섹션별 최소 분량 기준.

`evaluator.criteria.EVAL.TEXT_MIN` (80,000자)의 섹션별 분배.
검증기에 주입되어 '각 섹션이 충분히 쓰였는지' 평가.
SKILL.md §3.2 구현체.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SectionMinimum:
    """단일 섹션의 최소 품질 기준."""

    section_num: int
    title: str
    min_chars: int          # 본문 글자수 하한
    min_charts: int = 0     # SVG 차트 최소 개수
    min_tables: int = 0     # 테이블 최소 개수
    min_counter_args: int = 0  # counter_arg 블록 최소


#: 11섹션 + 2 특수(cover/appendix) 표준 분량.
#: 합계 = 82,000자 (TEXT_MIN 80,000 초과 여유 2,000자).
SECTION_MINIMA: Final[dict[int, SectionMinimum]] = {
    1: SectionMinimum(1, "기업개요", 3_000, min_charts=1, min_tables=2),
    2: SectionMinimum(2, "산업분석", 10_000, min_charts=4, min_tables=2),
    3: SectionMinimum(3, "투자포인트 I", 8_000, min_charts=3, min_tables=1,
                      min_counter_args=1),
    4: SectionMinimum(4, "투자포인트 II", 8_000, min_charts=3, min_tables=1,
                      min_counter_args=1),
    5: SectionMinimum(5, "투자포인트 III", 8_000, min_charts=3, min_tables=1,
                      min_counter_args=1),
    6: SectionMinimum(6, "재무분석", 7_000, min_charts=4, min_tables=4),
    7: SectionMinimum(7, "Peer 비교", 4_000, min_charts=3, min_tables=3),
    8: SectionMinimum(8, "실적추정", 7_000, min_charts=3, min_tables=4),
    9: SectionMinimum(9, "밸류에이션", 6_000, min_charts=3, min_tables=3),
    10: SectionMinimum(10, "리스크", 4_000, min_charts=2, min_tables=1,
                       min_counter_args=1),
    11: SectionMinimum(11, "Appendix", 17_000, min_charts=0, min_tables=8),
}


def total_min_chars() -> int:
    """모든 섹션 최소 분량 합."""
    return sum(m.min_chars for m in SECTION_MINIMA.values())


def total_min_charts() -> int:
    return sum(m.min_charts for m in SECTION_MINIMA.values())


def total_min_tables() -> int:
    return sum(m.min_tables for m in SECTION_MINIMA.values())
