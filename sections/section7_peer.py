"""섹션 7 — Peer 비교.

Peer 3~6개 (국내 + 글로벌). 멀티플/성장률/마진 3축 비교

권장: Peer 선정 근거 → 멀티플 벤치마크 → 프리미엄/디스카운트 근거
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 7


def build_section(config, data: SectionData) -> str:
    """Peer 비교 섹션 HTML 생성.

    권장 data 구성:
        charts: [멀티플 scatter, 성장률 bar, 마진 comparison]  tables: [Peer 멀티플 3종, 영업지표]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    return assemble_section(header, data)
