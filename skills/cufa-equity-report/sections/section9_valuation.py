"""섹션 9 — 밸류에이션.

PBR/PER/DCF/RIM 중 종목 특성에 맞는 방법 1~2개 선택. 선택 근거 명시, 배제 근거 명시

권장: 방법 선택 근거 → 가정 → Football field → Reverse DCF sanity check
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 9


def build_section(config, data: SectionData) -> str:
    """밸류에이션 섹션 HTML 생성.

    권장 data 구성:
        charts: [Football field, PER band, 민감도 heatmap]  tables: [WACC, 가정표, Implied PER]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
