"""섹션 2 — 산업분석.

구조·경쟁·성장·규제·지정학. 3단계 이상 추론 체인 권장.
필수: 10,000자+, 차트 4+, 테이블 2+.
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 2


def build_section(config, data: SectionData) -> str:
    """산업분석 섹션 HTML 생성.

    권장 data 구성:
        keywords: 산업 구조 / 경쟁 구도 / 성장 동인 / 규제 / 지정학
        narrative_html: TAM→SAM→SOM 분해, 밸류체인, 경쟁 5세력 분석
        charts: [시장규모 시계열, 경쟁사 M/S, 성장률 bump, 지역 분포]
        tables: [TAM 분해, Peer 비교]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
