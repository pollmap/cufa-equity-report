"""섹션 4 — 투자포인트 II.

두 번째 투자포인트. IP1과 독립적인 각도에서 접근

권장: 비용 구조 개선, 신사업, 해외 확장 등 IP1과 다른 축
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 4


def build_section(config, data: SectionData) -> str:
    """투자포인트 II 섹션 HTML 생성.

    권장 data 구성:
        charts: [원가 분해, 해외 매출 비중, ROE path]  tables: [세부 분해]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    if not data.counter_args:
        raise ValueError(
            f'section4_ipN: counter_args 1개+ 필수 (SMIC 반박 패턴). '
            f'SECTION_MINIMA[4].min_counter_args={meta.min_counter_args}'
        )
    return assemble_section(header, data)
