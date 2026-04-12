"""CUFA Builder — 메인 오케스트레이터.

`build_report()` 는 `StockConfig` + 섹션 생성자 시퀀스를 받아 HTML을 조립하고,
post-processing + Evaluator v3 ALL PASS 루프까지 한번에 수행한다.

v16.0: 7섹션 HF 구조, SMIC 문체 강제 폐기, Trade Ticket YAML 신설.
`config/{stock_code}.py` 에서 `StockConfig` 인스턴스를 만들어 넘기면 된다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from .css import gen_css
from .figure import reset_figures


class SectionBuilder(Protocol):
    """섹션 생성자 시그니처.

    `sections/*.py` 의 `build_section()` 함수들이 준수해야 하는 인터페이스.
    """

    def __call__(self, config) -> str:
        ...


@dataclass
class BuildContext:
    """빌드 실행 컨텍스트.

    Attributes:
        output_html: 누적되는 HTML 문자열
        warnings: 빌드 중 수집된 경고 (섹션 길이 미달 등)
    """

    output_html: str = ""
    warnings: list[str] = field(default_factory=list)

    def append(self, html: str) -> None:
        self.output_html += html


def build_report(
    config,
    section_builders: list[SectionBuilder],
    *,
    opinion: str = "BUY",
    target_price: float = 0,
    current_price: float = 0,
    post_process: Callable[[str], str] | None = None,
) -> BuildContext:
    """보고서 HTML 생성 오케스트레이터.

    Args:
        config: `StockConfig` 인스턴스 (종목 식별 + 빌더 입력)
        section_builders: `SectionBuilder` 시퀀스 (11+ 섹션)
        opinion: "BUY" / "HOLD" / "SELL" (sticky header 표시)
        target_price: 목표주가 (sticky header + upside 계산)
        current_price: 현재가
        post_process: 빌드 후 변환 훅. `smic_inject` 나 `protected_replace` 등
                      `html → html` 함수를 넘긴다.

    Returns:
        `BuildContext` — `.output_html` 에 완성된 HTML, `.warnings` 에 경고 리스트.
    """
    reset_figures()
    ctx = BuildContext()

    # Head + Sticky header
    ctx.append(_gen_head(config))
    ctx.append(_gen_sticky_header(
        company_name=config.company_name,
        ticker=config.stock_code,
        opinion=opinion,
        target=target_price,
        current=current_price,
    ))

    # Section bodies
    for builder in section_builders:
        ctx.append(builder(config))

    # Footer + Interactive JS
    ctx.append(_gen_report_close())
    ctx.append(_gen_interactive_js())
    ctx.append("</body>\n</html>")

    if post_process is not None:
        ctx.output_html = post_process(ctx.output_html)

    return ctx


def write_output(ctx: BuildContext, config) -> Path:
    """빌드 결과를 `{output_dir}/{company}_CUFA_보고서.html` 로 저장."""
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{config.company_name}_CUFA_보고서.html"
    out_path.write_text(ctx.output_html, encoding="utf-8")
    return out_path


# ─── 내부 HTML 프래그먼트 생성 ───────────────────────────────────────

def _gen_head(config) -> str:
    return (
        '<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{config.company_name} ({config.stock_code}) '
        f'— CUFA 기업분석보고서</title>\n'
        f'<style>{gen_css()}</style>\n'
        '</head>\n<body>\n<div class="report">\n'
    )


def _gen_sticky_header(
    company_name: str,
    ticker: str,
    opinion: str,
    target: float,
    current: float,
) -> str:
    upside = ((target - current) / current * 100) if current else 0
    upside_color = "var(--positive)" if upside >= 0 else "var(--negative)"
    return (
        f'<div class="sticky-header">\n'
        f'  <span style="font-weight:700;">{company_name} ({ticker})</span>\n'
        f'  <span>{opinion} · 목표 '
        f'<span style="color:var(--purple);font-weight:600;">{target:,.0f}원</span>'
        f' · 현재 {current:,.0f}원 · '
        f'<span style="color:{upside_color};">{upside:+.1f}%</span></span>\n'
        f'</div>\n'
    )


def _gen_report_close() -> str:
    return "</div>\n"  # .report div 닫기


def _gen_interactive_js() -> str:
    return (
        '<div id="reading-progress"></div>\n'
        '<button id="back-top" '
        'onclick="window.scrollTo({top:0,behavior:\'smooth\'})">↑</button>\n'
        '<div class="ai-watermark">'
        'AI-Assisted Research Report — CUFA × Nexus MCP</div>\n'
        "<script>\n"
        "(function(){\n"
        "  const bar=document.getElementById('reading-progress');\n"
        "  const btn=document.getElementById('back-top');\n"
        "  let ticking=false;\n"
        "  window.addEventListener('scroll',()=>{\n"
        "    if(!ticking){requestAnimationFrame(()=>{\n"
        "      const st=document.documentElement.scrollTop;\n"
        "      const sh=document.documentElement.scrollHeight-document.documentElement.clientHeight;\n"
        "      bar.style.width=Math.round((st/sh)*100)+'%';\n"
        "      btn.classList.toggle('show',st>400);\n"
        "      ticking=false;\n"
        "    });ticking=true;}\n"
        "  },{passive:true});\n"
        "})();\n"
        "</script>\n"
    )
