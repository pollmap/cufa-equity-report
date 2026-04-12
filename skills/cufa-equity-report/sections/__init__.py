"""CUFA Sections — 7섹션 HF 구조 (v16.0).

v15 11섹션 → v16 7섹션 전환.
분량 기반 SMIC 문체 구조 폐기 → 실행가능성 중심 HF 구조.

7-Section Structure:
    §1 BLUF           — Investment Summary (Bottom Line Up Front)
    §2 Thesis         — 3축 통합 투자 논리
    §3 Business Setup — 사업 구조 + 산업 설정
    §4 Numbers        — Financial + Peer + Estimate + Valuation
    §5 Risks          — Bear Case First + Kill Conditions
    §6 Trade          — Trade Implementation (⚡ 핵심)
    §7 Appendix       — 압축 Appendix (A-1~A-4)

사용 예시:
    from sections import SECTION_BUILDERS
    html = SECTION_BUILDERS[1](config, html_content)
"""

from .base import SectionData, assemble_section, close_section, render_chart_grid

from .section1_bluf import build_section as build_section1
from .section2_thesis import build_section as build_section2
from .section3_business_setup import build_section as build_section3
from .section4_numbers import build_section as build_section4
from .section5_risks import build_section as build_section5
from .section6_trade import build_section as build_section6
from .section7_appendix import build_section as build_section7


#: 번호 → 빌더 함수. SECTION_BUILDERS[n](config, html_content) 형식.
SECTION_BUILDERS: dict[int, object] = {
    1: build_section1,
    2: build_section2,
    3: build_section3,
    4: build_section4,
    5: build_section5,
    6: build_section6,
    7: build_section7,
}

#: 섹션 번호 → ID 매핑 (TOC 앵커용)
SECTION_IDS: dict[int, str] = {
    1: "s1_bluf",
    2: "s2_thesis",
    3: "s3_business",
    4: "s4_numbers",
    5: "s5_risks",
    6: "s6_trade",
    7: "s7_appendix",
}

#: 섹션 번호 → 한국어 제목
SECTION_TITLES: dict[int, str] = {
    1: "Investment Summary",
    2: "투자 Thesis",
    3: "Business & Industry Setup",
    4: "The Numbers",
    5: "Risks — Bear Case First",
    6: "Trade Implementation",
    7: "Appendix",
}

__all__ = [
    "SectionData",
    "SECTION_BUILDERS",
    "SECTION_IDS",
    "SECTION_TITLES",
    "assemble_section",
    "close_section",
    "render_chart_grid",
    "build_section1",
    "build_section2",
    "build_section3",
    "build_section4",
    "build_section5",
    "build_section6",
    "build_section7",
]
