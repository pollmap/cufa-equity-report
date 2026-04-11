"""섹션 1 — 기업개요.

순서: 사이드바 + 본문(창립 연혁·사업 구조·지배구조) → 사업부문 donut → 주주 테이블.
필수: 3,000자 이상, 차트 1+, 테이블 2+ (SECTION_MINIMA[1]).
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 1


def build_section(config, data: SectionData) -> str:
    """기업개요 섹션 HTML 생성.

    Args:
        config: `StockConfig` (company_name, stock_code 필요)
        data: `SectionData` — 권장 구성:
            keywords: [("회사 역사", "..."), ("주력사업", "..."),
                       ("지배구조", "..."), ("임직원", "...")]
            narrative_html: 창립 연혁 → 사업 모델 → 경영진 → 주주 현황 순
            charts: [사업부문 donut] (1개+)
            tables: [주요주주 표, 사업부 매출 분해 표] (2개+)
    """
    meta = SECTION_MINIMA[SEC_NUM]
    title = data.title_override or meta.title
    header = section_header(SEC_NUM, title, config.company_name, config.stock_code)
    return assemble_section(header, data, chart_cols=1)
