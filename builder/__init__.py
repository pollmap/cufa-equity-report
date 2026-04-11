"""CUFA Builder — HTML 보고서 빌드 엔진.

v15.0 모듈 구조:
    builder/
    ├── core.py           ← build_report() 오케스트레이터
    ├── css.py            ← gen_css() 단일 표준 CSS
    ├── design_tokens.py  ← CSS_VARS, CHART_COLOR_ROLES, BORDER_RADIUS
    ├── figure.py         ← FigureCounter, fig_num(), reset_figures()
    ├── svg.py            ← 32종 SVG 차트 헬퍼
    ├── helpers.py        ← section_header, sidebar_wrap, table
    ├── components.py     ← counter_arg, expand_card, chart_with_context
    └── markdown.py       ← md_to_html() 단순 마크다운 변환기

import 방법:
    from builder import (
        build_report, BuildContext, write_output,
        gen_css, fig_num, reset_figures,
        svg_bar, svg_line, svg_donut, ...,
        section_header, sidebar_wrap, table, backtest_result_table,
        counter_arg, expand_card, chart_with_context, add_source,
        md_to_html,
    )
"""
from .core import BuildContext, SectionBuilder, build_report, write_output
from .css import gen_css
from .design_tokens import (
    BORDER_RADIUS,
    CHART_COLOR_ROLES,
    CSS_VARS,
    DEFAULT_PALETTE,
    FONT_FAMILY,
)
from .figure import DEFAULT_COUNTER, FigureCounter, fig_num, reset_figures
from .markdown import md_to_html, read_md
from .helpers import (
    backtest_result_table,
    section_header,
    sidebar_wrap,
    table,
)
from .components import (
    add_source,
    chart_with_context,
    counter_arg,
    data_tip,
    expand_card,
    implied_per_check,
    proprietary_metric,
    scenario_tabs,
    valuation_rationale,
)
from .svg import (
    svg_area,
    svg_bar,
    svg_boxplot,
    svg_bubble_risk,
    svg_bullet,
    svg_bump,
    svg_candlestick,
    svg_donut,
    svg_flow_diagram,
    svg_football,
    svg_gantt,
    svg_gauge,
    svg_grouped_bar,
    svg_hbar,
    svg_heatmap,
    svg_histogram,
    svg_line,
    svg_lollipop,
    svg_marimekko,
    svg_pareto,
    svg_pictogram,
    svg_rebased_price,
    svg_roe_pbr_path,
    svg_sankey,
    svg_scatter,
    svg_slope,
    svg_sparkline,
    svg_timeline,
    svg_tornado,
    svg_treemap,
    svg_waffle,
    svg_waterfall,
)

__all__ = [
    # core
    "BuildContext",
    "SectionBuilder",
    "build_report",
    "write_output",
    # css / tokens
    "gen_css",
    "CSS_VARS",
    "CHART_COLOR_ROLES",
    "BORDER_RADIUS",
    "FONT_FAMILY",
    "DEFAULT_PALETTE",
    # figure
    "FigureCounter",
    "DEFAULT_COUNTER",
    "fig_num",
    "reset_figures",
    # markdown
    "md_to_html",
    "read_md",
    # helpers
    "section_header",
    "sidebar_wrap",
    "table",
    "backtest_result_table",
    # components
    "add_source",
    "chart_with_context",
    "counter_arg",
    "data_tip",
    "expand_card",
    "implied_per_check",
    "proprietary_metric",
    "scenario_tabs",
    "valuation_rationale",
    # svg (32종)
    "svg_area",
    "svg_bar",
    "svg_boxplot",
    "svg_bubble_risk",
    "svg_bullet",
    "svg_bump",
    "svg_candlestick",
    "svg_donut",
    "svg_flow_diagram",
    "svg_football",
    "svg_gantt",
    "svg_gauge",
    "svg_grouped_bar",
    "svg_hbar",
    "svg_heatmap",
    "svg_histogram",
    "svg_line",
    "svg_lollipop",
    "svg_marimekko",
    "svg_pareto",
    "svg_pictogram",
    "svg_rebased_price",
    "svg_roe_pbr_path",
    "svg_sankey",
    "svg_scatter",
    "svg_slope",
    "svg_sparkline",
    "svg_timeline",
    "svg_tornado",
    "svg_treemap",
    "svg_waffle",
    "svg_waterfall",
]
