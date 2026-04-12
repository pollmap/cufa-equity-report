"""§3 Business & Industry Setup — 사업 구조 + 산업 환경.

HF 구조 섹션 3. 비즈니스 모델과 산업 구조를 통합 서술한다.
매출 세그먼트 분해 → 경쟁 포지셔닝 → 해자 분석 → counter-arg.

포함 요소:
- 매출 세그먼트 테이블
- 경쟁 포지셔닝 / 해자 요약
- 산업 핵심 지표 (config.INDUSTRY_DATA)
- counter-arg 블록 (반론 1개+)
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§3 Business & Industry Setup 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). BUSINESS, INDUSTRY_DATA 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    business = getattr(config, "BUSINESS", {}) or {}
    industry = getattr(config, "INDUSTRY_DATA", {}) or {}

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")

    segments_html = _render_segments(business.get("segments", []))
    moat_html = _render_moat(business.get("moat", {}))
    key_metrics_html = _render_key_metrics(business.get("key_metrics", {}))
    industry_html = _render_industry(industry)
    counter_html = _render_counter(business)

    body = html_content or ""

    return f"""
<section class="section" id="s3_business">
  <div class="section-header">
    <div class="section-num">3</div>
    <div class="section-title">Business &amp; Industry Setup — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  {segments_html}
  {moat_html}
  {key_metrics_html}
  {industry_html}
  {counter_html}
  {body}
</section>
"""


def _render_segments(segments: list) -> str:
    if not segments:
        return ""
    rows = "".join(
        f"<tr><td>{s.get('name','')}</td><td>{s.get('revenue_pct','')}%</td>"
        f"<td>{s.get('margin_pct','')}</td><td>{s.get('description','')}</td></tr>"
        for s in segments
    )
    return f"""
<p style="font-size:13px;font-weight:700;margin:16px 0 8px">매출 세그먼트 구성</p>
<div class="table-scroll">
<table class="data">
  <thead><tr><th>사업부</th><th>매출 비중</th><th>마진율</th><th>특징</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


def _render_moat(moat: dict) -> str:
    if not moat:
        return ""
    moat_type = moat.get("type", "")
    description = moat.get("description", "")
    sources = moat.get("sources", []) or []
    items = "".join(
        f'<li style="margin-bottom:4px;font-size:11px">{s}</li>'
        for s in sources
    )
    sources_html = f'<ul style="margin:6px 0 0 14px;list-style:disc">{items}</ul>' if sources else ""
    return f"""
<div class="callout" style="margin:16px 0;padding:12px 16px;border-left:3px solid var(--amber);
     background:var(--surface);border-radius:2px">
  <div style="font-size:12px;font-weight:700;color:var(--amber);margin-bottom:6px">
    경제적 해자 — {moat_type}
  </div>
  <p style="font-size:12px;color:var(--text)">{description}</p>
  {sources_html}
</div>
"""


def _render_key_metrics(key_metrics: dict) -> str:
    if not key_metrics:
        return ""
    items = list(key_metrics.items())[:6]
    cards = "".join(
        f'<div class="metric-card"><div class="mc-label">{k}</div>'
        f'<div class="mc-value" style="font-size:14px">{v}</div></div>'
        for k, v in items
    )
    cols = min(len(items), 3)
    return f"""
<div class="metric-grid" style="grid-template-columns:repeat({cols},1fr);margin:16px 0">
  {cards}
</div>
"""


def _render_industry(industry: dict) -> str:
    if not industry:
        return ""
    overview = industry.get("overview", "")
    structure = industry.get("structure", "")
    drivers = industry.get("key_drivers", []) or []

    driver_items = "".join(
        f'<li style="margin-bottom:3px;font-size:11px;color:var(--text-sec)">{d}</li>'
        for d in drivers
    )
    drivers_html = (
        f'<ul style="margin:6px 0 0 14px;list-style:disc">{driver_items}</ul>'
        if drivers else ""
    )

    structure_html = (
        f'<p style="font-size:12px;color:var(--text-sec);margin-top:6px">{structure}</p>'
        if structure else ""
    )

    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px">산업 구조 분석</p>
<p style="font-size:12px;line-height:1.6;color:var(--text)">{overview}</p>
{structure_html}
{drivers_html}
"""


def _render_counter(business: dict) -> str:
    counter = business.get("counter_arg", business.get("bear_view", ""))
    if not counter:
        return """
<div class="counter-arg" style="margin-top:20px;padding:12px 16px;
     border-left:3px solid var(--negative);background:var(--surface);border-radius:2px">
  <div style="font-size:11px;font-weight:700;color:var(--negative);margin-bottom:6px">
    Bear View — 반론
  </div>
  <p style="font-size:12px;color:var(--text-sec)">BUSINESS.counter_arg 값을 설정하세요.</p>
</div>
"""
    return f"""
<div class="counter-arg" style="margin-top:20px;padding:12px 16px;
     border-left:3px solid var(--negative);background:var(--surface);border-radius:2px">
  <div style="font-size:11px;font-weight:700;color:var(--negative);margin-bottom:6px">
    Bear View — 반론
  </div>
  <p style="font-size:12px;color:var(--text)">{counter}</p>
</div>
"""
