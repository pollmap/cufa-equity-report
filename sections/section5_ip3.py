"""섹션 5 — 투자포인트 III.

세 번째 투자포인트. 선택적 — 종목 특성에 따라 생략 가능

권장: 주주환원 확대, M&A 시너지, 기술 해자 등
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 5


def build_section(config, data: SectionData) -> str:
    """투자포인트 III 섹션 HTML 생성.

    권장 data 구성:
        charts: [배당/자사주 추이, 시너지 예상치]  tables: [주주환원 계획]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    if not data.counter_args:
        raise ValueError(
            f'section5_ipN: counter_args 1개+ 필수 (SMIC 반박 패턴). '
            f'SECTION_MINIMA[5].min_counter_args={meta.min_counter_args}'
        )
    return assemble_section(header, data)
