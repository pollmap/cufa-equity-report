"""섹션 8 — 실적추정.

P×Q 분해로 매출 추정. 계정과목별 % of sales 로 원가 추정. Bull/Base/Bear 3시나리오

권장: 매출 drivers 상세 → 비용 drivers → 시나리오 민감도
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 8


def build_section(config, data: SectionData) -> str:
    """실적추정 섹션 HTML 생성.

    권장 data 구성:
        charts: [매출 추이+추정, ASP 트렌드, OPM 민감도]  tables 4+: [P×Q 테이블, 비용 breakdown, 3시나리오, 반증조건]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
