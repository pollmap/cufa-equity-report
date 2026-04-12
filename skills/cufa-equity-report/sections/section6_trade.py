"""§6 Trade Implementation — 가장 중요한 섹션.

HF 구조 섹션 6. 실제 트레이드 실행 계획. Trade Ticket 박스,
YAML 코드 블록, 백테스트 결과 참조, QuantPipeline 연동 정보를 포함한다.

포함 요소:
- Trade Ticket 박스 (.ticket-box)
- Trade Ticket YAML 코드 블록 (.ticket-yaml)
- 진입/목표/손절 가격 시각화
- Backtest / QuantPipeline 참조 메모
- 포지션 사이징 근거
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§6 Trade Implementation 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). trade_ticket 또는 TRADE_TICKET 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    # 소문자/대문자 둘 다 허용
    tt = getattr(config, "trade_ticket", None) or getattr(config, "TRADE_TICKET", {}) or {}
    price_data = getattr(config, "PRICE", {}) or {}

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")
    current = price_data.get("current", 0)

    ticket_html = _render_ticket_box(tt, current, ticker)
    yaml_html = _render_ticket_yaml(tt, ticker, company)
    backtest_html = _render_backtest_note(tt)

    body = html_content or ""

    return f"""
<section class="section" id="s6_trade">
  <div class="section-header">
    <div class="section-num">6</div>
    <div class="section-title">Trade Implementation — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  <div class="callout" style="border-left:3px solid var(--purple);background:var(--surface);
       padding:10px 16px;margin-bottom:20px;border-radius:2px">
    <p style="font-size:11px;color:var(--purple-light);font-weight:700">
      Trade Implementation은 이 보고서의 핵심 산출물이다.
      모든 분석은 여기 Trade Ticket 한 장으로 수렴해야 한다.
    </p>
  </div>

  {ticket_html}
  {yaml_html}
  {backtest_html}
  {body}
</section>
"""


def _render_ticket_box(tt: dict, current: float, ticker: str) -> str:
    opinion = tt.get("opinion", "HOLD")
    entry = tt.get("entry_price", tt.get("current_price", current))
    stop = tt.get("stop_loss", 0)
    target = tt.get("target_price", 0)
    horizon = tt.get("horizon_months", tt.get("horizon", ""))   # v16 schema: horizon_months
    if horizon:
        horizon = f"{horizon}개월" if str(horizon).isdigit() else str(horizon)
    pos_pct = tt.get("position_size_pct", 3.0)
    rr = tt.get("risk_reward", 0)
    rationale = tt.get("rationale", tt.get("reason", ""))

    opinion_color = {
        "BUY": "var(--positive)",
        "SELL": "var(--negative)",
        "HOLD": "var(--amber)",
    }.get(opinion.upper(), "var(--text-sec)")

    def fmt_price(v: Any) -> str:
        try:
            return f"{int(float(v)):,}원"
        except (TypeError, ValueError):
            return str(v)

    def fmt_rr(v: Any) -> str:
        try:
            return f"{float(v):.2f}x"
        except (TypeError, ValueError):
            return str(v)

    # 수익/손실 계산
    upside_html = ""
    if entry and target:
        try:
            up = (float(target) - float(entry)) / float(entry) * 100
            upside_html = f'<span style="color:var(--positive);font-size:11px">(+{up:.1f}%)</span>'
        except (TypeError, ValueError, ZeroDivisionError):
            pass

    downside_html = ""
    if entry and stop:
        try:
            dn = (float(stop) - float(entry)) / float(entry) * 100
            downside_html = f'<span style="color:var(--negative);font-size:11px">({dn:.1f}%)</span>'
        except (TypeError, ValueError, ZeroDivisionError):
            pass

    return f"""
<div class="ticket-box" style="border:2px solid var(--purple);border-radius:2px;
     background:var(--surface);padding:20px;margin-bottom:20px">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
    <div style="font-size:16px;font-weight:800;color:var(--text)">
      TRADE TICKET — {ticker}
    </div>
    <div style="font-size:28px;font-weight:900;color:{opinion_color}">{opinion}</div>
  </div>

  <div class="metric-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:16px">
    <div class="metric-card">
      <div class="mc-label">진입가 (Entry)</div>
      <div class="mc-value">{fmt_price(entry)}</div>
    </div>
    <div class="metric-card">
      <div class="mc-label">목표가 (Target)</div>
      <div class="mc-value" style="color:var(--positive)">{fmt_price(target)} {upside_html}</div>
    </div>
    <div class="metric-card">
      <div class="mc-label">손절가 (Stop Loss)</div>
      <div class="mc-value" style="color:var(--negative)">{fmt_price(stop)} {downside_html}</div>
    </div>
    <div class="metric-card">
      <div class="mc-label">Risk/Reward</div>
      <div class="mc-value">{fmt_rr(rr)}</div>
    </div>
  </div>

  <div style="display:flex;gap:12px;margin-bottom:12px">
    <div style="flex:1;padding:10px;background:var(--surface2);border-radius:2px">
      <div style="font-size:10px;color:var(--text-sec);margin-bottom:3px">투자 지평 (Horizon)</div>
      <div style="font-size:13px;font-weight:600">{horizon}</div>
    </div>
    <div style="flex:1;padding:10px;background:var(--surface2);border-radius:2px">
      <div style="font-size:10px;color:var(--text-sec);margin-bottom:3px">포지션 비중</div>
      <div style="font-size:13px;font-weight:600;color:var(--purple-light)">{pos_pct}%</div>
    </div>
  </div>

  {'<p style="font-size:12px;color:var(--text-sec);border-top:1px solid var(--border);padding-top:10px">' + rationale + '</p>' if rationale else ''}
</div>
"""


def _render_ticket_yaml(tt: dict, ticker: str, company: str) -> str:
    opinion = tt.get("opinion", "HOLD")
    entry = tt.get("entry_price", tt.get("current_price", ""))
    stop = tt.get("stop_loss", "")
    target = tt.get("target_price", "")
    horizon = tt.get("horizon_months", tt.get("horizon", ""))   # v16 schema: horizon_months
    if horizon:
        horizon = f"{horizon}개월" if str(horizon).isdigit() else str(horizon)
    pos_pct = tt.get("position_size_pct", 3.0)
    rr = tt.get("risk_reward", "")
    rationale = tt.get("rationale", tt.get("reason", ""))

    yaml_str = (
        f"ticker: {ticker}\n"
        f"company: {company}\n"
        f"opinion: {opinion}\n"
        f"entry_price: {entry}\n"
        f"stop_loss: {stop}\n"
        f"target_price: {target}\n"
        f"horizon: {horizon}\n"
        f"position_size_pct: {pos_pct}\n"
        f"risk_reward: {rr}\n"
        f"rationale: |\n"
        f"  {rationale}"
    )

    return f"""
<p style="font-size:12px;font-weight:700;margin:0 0 8px;color:var(--text-sec)">
  Trade Ticket YAML (QuantPipeline 입력 형식)
</p>
<pre class="ticket-yaml" style="background:#0d1117;border:1px solid var(--border);
     border-radius:2px;padding:14px 16px;font-size:11px;line-height:1.6;
     color:#e6edf3;overflow-x:auto;white-space:pre-wrap;font-family:monospace">{yaml_str}</pre>
"""


def _render_backtest_note(tt: dict) -> str:
    backtest_ref = tt.get("backtest_ref", "")
    quant_strategy = tt.get("quant_strategy", "")

    if not backtest_ref and not quant_strategy:
        return f"""
<div class="callout" style="margin-top:16px;padding:12px 16px;
     border-left:3px solid var(--blue);background:var(--surface);border-radius:2px">
  <div style="font-size:11px;font-weight:700;color:var(--blue);margin-bottom:4px">
    QuantPipeline / backtest 연동
  </div>
  <p style="font-size:11px;color:var(--text-sec)">
    trade_ticket.backtest_ref 와 trade_ticket.quant_strategy 를 설정하면
    QuantPipeline backtest 결과 링크가 자동으로 표시됩니다.
    (~/Desktop/open-trading-api/backtester/core/pipeline.py)
  </p>
</div>
"""

    strategy_html = (
        f'<p style="font-size:11px;color:var(--text-sec);margin-top:4px">'
        f"전략: <strong>{quant_strategy}</strong></p>"
        if quant_strategy else ""
    )
    ref_html = (
        f'<p style="font-size:11px;margin-top:6px">'
        f'<a href="{backtest_ref}" style="color:var(--blue)">backtest 결과 링크</a></p>'
        if backtest_ref else ""
    )

    return f"""
<div class="callout" style="margin-top:16px;padding:12px 16px;
     border-left:3px solid var(--blue);background:var(--surface);border-radius:2px">
  <div style="font-size:11px;font-weight:700;color:var(--blue);margin-bottom:4px">
    QuantPipeline backtest 참조
  </div>
  {strategy_html}
  {ref_html}
</div>
"""
