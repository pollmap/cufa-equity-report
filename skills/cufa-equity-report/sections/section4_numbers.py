"""§4 The Numbers — 재무 + Peer + 추정 + 밸류에이션 통합.

HF 구조 섹션 4. 수치 중심 섹션. 핵심 IS 요약, Peer 비교,
Football Field 밸류에이션, 민감도 분석을 단일 섹션에 통합한다.

포함 요소:
- IS CFS 요약 테이블 (실적 + 2개년 추정)
- Peer 비교 테이블 (Fwd PER, PBR, ROE, OPM)
- Football Field 서술 + TP 요약
- 민감도 (sensitivity) 매트릭스
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§4 The Numbers 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). IS_CFS, PEERS, WACC, TARGET_PRICE 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    is_cfs = getattr(config, "IS_CFS", []) or []
    peers = getattr(config, "PEERS", []) or []
    wacc = getattr(config, "WACC", {}) or {}
    target = getattr(config, "TARGET_PRICE", {}) or {}

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")

    is_html = _render_is_table(is_cfs)
    peer_html = _render_peer_table(peers)
    ff_html = _render_football_field(target, wacc)
    sensitivity_html = _render_sensitivity(target)

    body = html_content or ""

    return f"""
<section class="section" id="s4_numbers">
  <div class="section-header">
    <div class="section-num">4</div>
    <div class="section-title">The Numbers — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  {is_html}
  {peer_html}
  {ff_html}
  {sensitivity_html}
  {body}
</section>
"""


def _render_is_table(is_cfs: list) -> str:
    if not is_cfs:
        return '<p style="color:var(--text-sec);margin-bottom:12px">IS_CFS 데이터 없음.</p>'

    years = [row.get("year", "") for row in is_cfs]
    header_cells = "".join(f"<th>{y}</th>" for y in years)

    def row_html(label: str, key: str, fmt: str = "{:,.0f}") -> str:
        cells = ""
        for r in is_cfs:
            val = r.get(key, "")
            try:
                cells += f"<td>{fmt.format(float(val))}</td>"
            except (TypeError, ValueError):
                cells += f"<td>{val}</td>"
        return f"<tr><td>{label}</td>{cells}</tr>"

    est_note = "E = 추정치 (Forward)"
    return f"""
<p style="font-size:13px;font-weight:700;margin:0 0 8px">IS 연결 요약 (CFS 기준)</p>
<div class="table-scroll">
<table class="data">
  <thead><tr><th>구분 (억원)</th>{header_cells}</tr></thead>
  <tbody>
    {row_html("매출액", "revenue")}
    {row_html("영업이익", "operating_profit")}
    {row_html("영업이익률(%)", "opm", "{:.1f}")}
    {row_html("순이익(지배)", "net_profit")}
    {row_html("EPS(원)", "eps", "{:,.0f}")}
  </tbody>
</table>
</div>
<p style="font-size:10px;color:var(--text-sec);text-align:right;margin-top:2px">
  출처: DART(연결재무제표), Nexus MCP. {est_note}
</p>
"""


def _render_peer_table(peers: list) -> str:
    if not peers:
        return ""

    rows = ""
    for p in peers:
        name = p.get("name", "")
        fwd_per = p.get("fwd_per", "-")
        pbr = p.get("pbr", "-")
        roe = p.get("roe", "-")
        opm = p.get("opm", "-")
        note = p.get("note", "")

        def fmt(v: Any) -> str:
            try:
                return f"{float(v):.1f}x" if "x" not in str(v) else str(v)
            except (TypeError, ValueError):
                return str(v)

        rows += (
            f"<tr><td>{name}</td><td>{fmt(fwd_per)}</td><td>{fmt(pbr)}</td>"
            f"<td>{fmt(roe)}</td><td>{fmt(opm)}</td><td>{note}</td></tr>"
        )

    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px">Peer 비교 (Fwd 기준 — Forward 컨센서스)</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr><th>기업</th><th>Fwd PER</th><th>PBR (Trailing)</th>
        <th>ROE (%)</th><th>OPM (%)</th><th>비고</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
<p style="font-size:10px;color:var(--text-sec);text-align:right;margin-top:2px">
  출처: Bloomberg Consensus / Nexus MCP. 기준: 12MF Forward
</p>
"""


def _render_football_field(target: dict, wacc: dict) -> str:
    weighted = target.get("weighted", 0)
    upside = target.get("upside_pct", 0)
    methods = target.get("methods", []) or []
    wacc_val = wacc.get("wacc_pct", wacc.get("wacc", ""))
    terminal_g = wacc.get("terminal_growth", "")

    method_rows = ""
    for m in methods:
        mname = m.get("method", "")
        mtp = m.get("target_price", "")
        mwt = m.get("weight_pct", "")
        try:
            method_rows += (
                f"<tr><td>{mname}</td><td>{float(mtp):,.0f}원</td>"
                f"<td>{float(mwt):.0f}%</td></tr>"
            )
        except (TypeError, ValueError):
            method_rows += f"<tr><td>{mname}</td><td>{mtp}</td><td>{mwt}</td></tr>"

    methods_table = ""
    if method_rows:
        methods_table = f"""
<table class="data" style="max-width:420px;margin-top:8px">
  <thead><tr><th>방법론</th><th>산출 TP</th><th>가중치</th></tr></thead>
  <tbody>{method_rows}</tbody>
</table>"""

    wacc_note = ""
    if wacc_val or terminal_g:
        wacc_note = (
            f'<p style="font-size:11px;color:var(--text-sec);margin-top:6px">'
            f"WACC {wacc_val}% | Terminal Growth {terminal_g}%</p>"
        )

    # Football field — 민감도 서술 영역
    return f"""
<div style="margin:24px 0;padding:16px;border:1px solid var(--border);
     background:var(--surface);border-radius:2px">
  <p style="font-size:13px;font-weight:700;margin-bottom:10px">
    Football Field 밸류에이션 요약
  </p>
  <div class="metric-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:12px">
    <div class="metric-card">
      <div class="mc-label">가중 목표주가 (TP)</div>
      <div class="mc-value" style="font-size:18px">{weighted:,}원</div>
    </div>
    <div class="metric-card">
      <div class="mc-label">업사이드</div>
      <div class="mc-value" style="color:var(--positive)">{upside:+.1f}%</div>
    </div>
    <div class="metric-card">
      <div class="mc-label">Football 기준</div>
      <div class="mc-value" style="font-size:12px">다중 방법론 평균</div>
    </div>
  </div>
  {methods_table}
  {wacc_note}
</div>
"""


def _render_sensitivity(target: dict) -> str:
    sensitivity = target.get("sensitivity", []) or []
    if not sensitivity:
        return f"""
<div class="callout" style="margin:12px 0;padding:12px;border-left:3px solid var(--amber);
     background:var(--surface);border-radius:2px">
  <p style="font-size:12px;color:var(--text-sec)">
    민감도(sensitivity) 분석: TARGET_PRICE.sensitivity 리스트를 채우면 테이블이 자동 생성됩니다.
    예: [{{"variable":"매출성장률","base":"15%","bear":"5%","bull":"25%","tp_impact":"±100,000원"}}]
  </p>
</div>
"""

    rows = "".join(
        f"<tr><td>{s.get('variable','')}</td><td>{s.get('bear','')}</td>"
        f"<td>{s.get('base','')}</td><td>{s.get('bull','')}</td>"
        f"<td>{s.get('tp_impact','')}</td></tr>"
        for s in sensitivity
    )
    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px">민감도 분석 (Key Assumption vs TP)</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr><th>핵심 가정</th><th>Bear</th><th>Base</th><th>Bull</th><th>TP 영향</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""
