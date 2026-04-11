"""섹션 11 — Appendix.

16개+ 부록 테이블 (A-1 ~ A-16+). 재무상세, 추정상세, Peer 세부, 산업 체크리스트, 데이터출처

권장: Appendix A-1 ~ A-16 로 넘버링, min 8 tables + 데이터출처 섹션
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 11


def build_section(config, data: SectionData) -> str:
    """Appendix 섹션 HTML 생성.

    권장 data 구성:
        tables 8+: [IS 10년, BS 10년, CF 10년, Peer 세부, P×Q 세부, WACC 세부, 민감도 매트릭스, 데이터출처]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
