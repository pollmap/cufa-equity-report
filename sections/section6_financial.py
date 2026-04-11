"""섹션 6 — 재무분석.

IS/BS/CF 5개년 + DuPont + Kitchen Sinking 체크. Plus α (OCF/NI, Accruals Ratio)

권장: IS 5개년 → ROE 분해 → 현금흐름 품질 → 재무건전성
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 6


def build_section(config, data: SectionData) -> str:
    """재무분석 섹션 HTML 생성.

    권장 data 구성:
        charts: [매출/영업익 bar, ROE 분해, FCF 트렌드, 차입금 비율]  tables 4+: [IS, BS, CF, 주요비율]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
