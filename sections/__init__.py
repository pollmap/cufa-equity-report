"""CUFA Sections — 11섹션 생성자 + 공통 데이터 모델.

사용 예시:
    from sections import (
        SectionData, SECTION_MINIMA,
        build_section1, build_section2, ..., build_section11,
    )

    data1 = SectionData(keywords=[...], narrative_html="...", charts=[...])
    html1 = build_section1(config, data1)

각 section_N.build_section() 은 동일한 시그니처 `(config, data) -> str`.
"""
from .base import SectionData, assemble_section, close_section, render_chart_grid
from .minima import (
    SECTION_MINIMA,
    SectionMinimum,
    total_min_chars,
    total_min_charts,
    total_min_tables,
)

from .section1_company import build_section as build_section1
from .section2_industry import build_section as build_section2
from .section3_ip1 import build_section as build_section3
from .section4_ip2 import build_section as build_section4
from .section5_ip3 import build_section as build_section5
from .section6_financial import build_section as build_section6
from .section7_peer import build_section as build_section7
from .section8_estimate import build_section as build_section8
from .section9_valuation import build_section as build_section9
from .section10_risk import build_section as build_section10
from .section11_appendix import build_section as build_section11


#: 번호 → 빌더 함수 매핑. 동적 호출 시 `SECTION_BUILDERS[3](config, data)` 식으로.
SECTION_BUILDERS = {
    1: build_section1,
    2: build_section2,
    3: build_section3,
    4: build_section4,
    5: build_section5,
    6: build_section6,
    7: build_section7,
    8: build_section8,
    9: build_section9,
    10: build_section10,
    11: build_section11,
}

__all__ = [
    "SectionData",
    "SectionMinimum",
    "SECTION_MINIMA",
    "SECTION_BUILDERS",
    "assemble_section",
    "close_section",
    "render_chart_grid",
    "total_min_chars",
    "total_min_charts",
    "total_min_tables",
    "build_section1",
    "build_section2",
    "build_section3",
    "build_section4",
    "build_section5",
    "build_section6",
    "build_section7",
    "build_section8",
    "build_section9",
    "build_section10",
    "build_section11",
]
