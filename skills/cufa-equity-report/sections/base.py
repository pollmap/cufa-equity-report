"""CUFA Sections — 공용 데이터 모델 + 렌더 헬퍼.

각 section_N.py 파일은 `SectionData` 인스턴스를 받아 HTML을 생성한다.
섹션 닫기(`</div>`) 는 `close_section()` 에서 일괄 처리.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class SectionData:
    """섹션 렌더러에 주입되는 콘텐츠 데이터.

    Attributes:
        keywords: 사이드바 키워드 `[(head, val), ...]` — 3~6개 권장
        narrative_html: 사이드바 우측 본문 HTML (p, strong 포함)
        charts: 섹션 본문 아래 배치할 SVG HTML 시퀀스
        tables: 테이블 HTML 시퀀스
        counter_args: counter_arg 블록 HTML 시퀀스 (IP 섹션에서 IP당 1개+)
        extra_blocks: proprietary_metric, callout 등 기타 구조 HTML
        title_override: 섹션 제목 오버라이드 (기본은 SECTION_MINIMA 기준)
    """

    keywords: Sequence[tuple[str, str]] = field(default_factory=list)
    narrative_html: str = ""
    charts: Sequence[str] = field(default_factory=list)
    tables: Sequence[str] = field(default_factory=list)
    counter_args: Sequence[str] = field(default_factory=list)
    extra_blocks: Sequence[str] = field(default_factory=list)
    title_override: str | None = None


def close_section() -> str:
    """섹션 div 닫기. 모든 section_N.build_section() 끝에서 호출."""
    return "</div>\n"


def render_chart_grid(charts: Sequence[str], cols: int = 2) -> str:
    """차트 여러 개를 `cols` 열 그리드로 배치.

    2열은 `.chart-pair`, 그 외는 `.chart-grid` 클래스 사용.
    """
    if not charts:
        return ""
    if cols == 2:
        out: list[str] = []
        i = 0
        while i < len(charts):
            pair = charts[i:i + 2]
            out.append('<div class="chart-pair">')
            out.extend(pair)
            out.append("</div>")
            i += 2
        return "\n".join(out) + "\n"
    return "\n".join(charts) + "\n"


def render_table_block(tables: Sequence[str]) -> str:
    """테이블 시퀀스를 순차 렌더링 (사이 여백 자동)."""
    if not tables:
        return ""
    return "\n".join(tables) + "\n"


def assemble_section(
    header_html: str,
    data: SectionData,
    *,
    chart_cols: int = 2,
) -> str:
    """공통 섹션 조립 파이프라인.

    header (사이드바 래핑된 본문 + 차트 그리드 + 테이블 + 추가 블록 + counter_args) + close.

    개별 section_N 이 이 헬퍼를 호출하기만 하면 되므로 보일러플레이트 제거.
    """
    from builder.helpers import sidebar_wrap

    parts: list[str] = [header_html]
    if data.narrative_html or data.keywords:
        parts.append(sidebar_wrap(data.keywords, data.narrative_html))
    parts.append(render_chart_grid(data.charts, cols=chart_cols))
    parts.append(render_table_block(data.tables))
    parts.extend(data.extra_blocks)
    parts.extend(data.counter_args)
    parts.append(close_section())
    return "".join(parts)
