"""섹션 10 — 리스크.

리스크 5~8개. Bubble risk 차트로 확률×영향도 시각화. counter_arg 1개+

권장: 리스크 매트릭스 → 각 리스크별 반증조건 → Kill condition
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 10


def build_section(config, data: SectionData) -> str:
    """리스크 섹션 HTML 생성.

    권장 data 구성:
        charts: [Bubble risk, 시나리오별 손실]  tables: [Kill conditions]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    if not data.counter_args:
        raise ValueError(
            f'section10_ipN: counter_args 1개+ 필수 (SMIC 반박 패턴). '
            f'SECTION_MINIMA[10].min_counter_args={meta.min_counter_args}'
        )
    return assemble_section(header, data)
