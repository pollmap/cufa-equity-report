"""섹션 3 — 투자포인트 I.

첫 번째 투자포인트. 4단계 이상 추론 체인 + 인라인 반박 + counter_arg 블록 1개+

권장: 트렌드 → 구조적 변화 → 기업 포지셔닝 → 수익 영향 → 리레이팅
"""
from __future__ import annotations

from builder.helpers import section_header

from .base import SectionData, assemble_section
from .minima import SECTION_MINIMA

SEC_NUM = 3


def build_section(config, data: SectionData) -> str:
    """투자포인트 I 섹션 HTML 생성.

    권장 data 구성:
        charts: [성장 시계열, 점유율 변화, 마진 분해]  tables: [시나리오 민감도]
    """
    meta = SECTION_MINIMA[SEC_NUM]
    header = section_header(
        SEC_NUM, data.title_override or meta.title,
        config.company_name, config.stock_code,
    )
    if not data.counter_args:
        raise ValueError(
            f'section3_ipN: counter_args 1개+ 필수 (SMIC 반박 패턴). '
            f'SECTION_MINIMA[3].min_counter_args={meta.min_counter_args}'
        )
    return assemble_section(header, data)
