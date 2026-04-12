"""§1 BLUF — Investment Summary (Bottom Line Up Front).

HF 구조 섹션 1. 보고서의 첫 번째 섹션으로 핵심 결론을 먼저 제시한다.
독자가 이 섹션만 읽어도 투자 판단을 내릴 수 있어야 한다.

포함 요소:
- 투자의견 / TP / SL / Risk-Reward
- 3축 Thesis 요약 (1줄씩)
- Bear Case 최악 시나리오 가격
- 촉매 타임라인 (3건+)
- Trade Ticket 미리보기
"""

from __future__ import annotations
from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """
    §1 BLUF 섹션 HTML 생성.

    Args:
        config:       StockConfig (v16). trade_ticket / kill_conditions 포함.
        html_content: 본문 서술 HTML (선택). 없으면 기본 구조만.

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    price_data = getattr(config, "PRICE", {}) or {}
    target_data = getattr(config, "TARGET_PRICE", {}) or {}
    tt = getattr(config, "trade_ticket", {}) or {}
    thesis = getattr(config, "THESIS", []) or []
    catalysts = getattr(config, "CATALYST_TIMELINE", []) or []
    scenario = getattr(config, "VALUATION_SCENARIOS", {}) or {}

    ticker = meta.get("ticker", "")
    company = meta.get("company_name", meta.get("name", ""))
    current = price_data.get("current", 0)
    target_wt = target_data.get("weighted", 0)
    upside = target_data.get("upside_pct", 0)
    rr = target_data.get("risk_reward", tt.get("risk_reward", 0))

    opinion = tt.get("opinion", "HOLD")
    stop = tt.get("stop_loss", 0)
    pos_pct = tt.get("position_size_pct", 3.0)

    bear_price = scenario.get("bear", {}).get("price", 0)
    opinion_class = {"BUY": "buy", "SELL": "sell"}.get(opinion.upper(), "hold")

    # Key Metrics row
    metrics_html = f"""
<div class="metric-grid" style="grid-template-columns:repeat(5,1fr)">
  <div class="metric-card">
    <div class="mc-label">투자의견</div>
    <div class="mc-value {opinion_class}" style="font-size:22px">{opinion}</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">목표주가 (TP)</div>
    <div class="mc-value">{target_wt:,}원</div>
    <div style="font-size:10px;color:var(--positive)">Upside {upside:+.1f}%</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">현재가</div>
    <div class="mc-value">{current:,}원</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">손절가 (SL)</div>
    <div class="mc-value" style="color:var(--negative)">{stop:,}원</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">Risk/Reward</div>
    <div class="mc-value">{rr:.2f}x</div>
    <div style="font-size:10px;color:var(--text-sec)">비중 {pos_pct:.1f}%</div>
  </div>
</div>"""

    # 3축 Thesis
    thesis_html = ""
    if thesis:
        axes = thesis[:3]
        thesis_html = '<div class="thesis-box">'
        for i, ax in enumerate(axes, 1):
            title = ax.get("title", ax) if isinstance(ax, dict) else str(ax)
            thesis_html += f"""
  <div class="thesis-axis">
    <div class="axis-num">{i}</div>
    <div class="axis-text"><strong>{title}</strong></div>
  </div>"""
        thesis_html += "</div>"

    # Catalyst Timeline
    cat_html = ""
    if catalysts:
        rows = "".join(
            f'<tr><td>{c.get("date","")}</td><td>{c.get("event","")}</td></tr>'
            for c in catalysts[:5]
        )
        cat_html = f"""
<table class="data" style="margin-top:12px">
  <thead><tr><th>일자</th><th>Catalyst 이벤트</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""

    # Bear Case warning
    bear_html = ""
    if bear_price:
        bear_html = f"""
<div class="callout" style="border-left-color:var(--negative);background:#fef2f2">
  <p style="color:var(--negative)">
    Bear Case 하방: <strong>{bear_price:,}원</strong>
    {f"({(bear_price-current)/current*100:+.1f}% vs 현재가)" if current else ""}
    — SL 이하로 붕괴 시 즉시 청산
  </p>
</div>"""

    body = html_content or ""

    return f"""
<section class="section" id="s1_bluf">
  <div class="section-header">
    <div class="section-num">1</div>
    <div class="section-title">Investment Summary — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  {metrics_html}
  {thesis_html}
  {bear_html}
  {cat_html}
  {body}
</section>
"""
