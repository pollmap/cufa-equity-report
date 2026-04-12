"""§7 Appendix — 부록 데이터 테이블 + 출처 + Compliance Notice.

HF 구조 섹션 7. 본문 섹션에서 생략된 상세 수치를 제공한다.
AI-Assisted 워터마크, 데이터 출처 명시, Compliance Notice를 포함한다.

포함 요소:
- A-1 IS 연결 요약
- A-2 BS 연결 요약
- A-3 현금흐름 요약
- A-4 Peer 세부 비교
- 데이터 출처 (Data Sources / 출처)
- Compliance Notice
- AI-Assisted 워터마크
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§7 Appendix 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). IS_CFS, BS_CFS, PEERS 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    is_cfs = getattr(config, "IS_CFS", []) or []
    bs_cfs = getattr(config, "BS_CFS", []) or []
    cf_cfs = getattr(config, "CF_CFS", []) or []
    peers = getattr(config, "PEERS", []) or []

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")
    report_date = meta.get("report_date", "")

    a1_html = _render_a1_is(is_cfs)
    a2_html = _render_a2_bs(bs_cfs)
    a3_html = _render_a3_cf(cf_cfs)
    a4_html = _render_a4_peers(peers)
    sources_html = _render_sources(meta)
    compliance_html = _render_compliance(company, ticker, report_date)

    body = html_content or ""

    return f"""
<section class="section" id="s7_appendix">
  <div class="section-header">
    <div class="section-num">7</div>
    <div class="section-title">Appendix — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  {a1_html}
  {a2_html}
  {a3_html}
  {a4_html}
  {body}
  {sources_html}
  {compliance_html}
</section>
"""


def _render_a1_is(is_cfs: list) -> str:
    if not is_cfs:
        return '<p style="color:var(--text-sec);margin-bottom:16px">A-1: IS_CFS 데이터 없음.</p>'

    years = [r.get("year", "") for r in is_cfs]
    header = "".join(f"<th>{y}</th>" for y in years)

    def row(label: str, key: str) -> str:
        cells = ""
        for r in is_cfs:
            val = r.get(key, "")
            try:
                cells += f"<td>{float(val):,.0f}</td>"
            except (TypeError, ValueError):
                cells += f"<td>{val}</td>"
        return f"<tr><td>{label}</td>{cells}</tr>"

    return f"""
<p style="font-size:12px;font-weight:700;margin:16px 0 6px;color:var(--purple-light)">
  A-1. 손익계산서 요약 (연결 CFS 기준, 억원)
</p>
<div class="table-scroll">
<table class="data">
  <thead><tr><th>항목</th>{header}</tr></thead>
  <tbody>
    {row("매출액", "revenue")}
    {row("매출원가", "cogs")}
    {row("매출총이익", "gross_profit")}
    {row("영업이익", "operating_profit")}
    {row("영업이익률(%)", "opm")}
    {row("세전이익", "pretax_income")}
    {row("순이익(지배)", "net_profit")}
    {row("EPS(원)", "eps")}
  </tbody>
</table>
</div>
"""


def _render_a2_bs(bs_cfs: list) -> str:
    if not bs_cfs:
        return ""

    years = [r.get("year", "") for r in bs_cfs]
    header = "".join(f"<th>{y}</th>" for y in years)

    def row(label: str, key: str) -> str:
        cells = ""
        for r in bs_cfs:
            val = r.get(key, "")
            try:
                cells += f"<td>{float(val):,.0f}</td>"
            except (TypeError, ValueError):
                cells += f"<td>{val}</td>"
        return f"<tr><td>{label}</td>{cells}</tr>"

    return f"""
<p style="font-size:12px;font-weight:700;margin:20px 0 6px;color:var(--purple-light)">
  A-2. 재무상태표 요약 (연결 CFS 기준, 억원)
</p>
<div class="table-scroll">
<table class="data">
  <thead><tr><th>항목</th>{header}</tr></thead>
  <tbody>
    {row("총자산", "total_assets")}
    {row("유동자산", "current_assets")}
    {row("비유동자산", "non_current_assets")}
    {row("총부채", "total_liabilities")}
    {row("유동부채", "current_liabilities")}
    {row("자본총계", "total_equity")}
    {row("부채비율(%)", "debt_ratio")}
  </tbody>
</table>
</div>
"""


def _render_a3_cf(cf_cfs: list) -> str:
    if not cf_cfs:
        return ""

    years = [r.get("year", "") for r in cf_cfs]
    header = "".join(f"<th>{y}</th>" for y in years)

    def row(label: str, key: str) -> str:
        cells = ""
        for r in cf_cfs:
            val = r.get(key, "")
            try:
                cells += f"<td>{float(val):,.0f}</td>"
            except (TypeError, ValueError):
                cells += f"<td>{val}</td>"
        return f"<tr><td>{label}</td>{cells}</tr>"

    return f"""
<p style="font-size:12px;font-weight:700;margin:20px 0 6px;color:var(--purple-light)">
  A-3. 현금흐름 요약 (연결 CFS 기준, 억원)
</p>
<div class="table-scroll">
<table class="data">
  <thead><tr><th>항목</th>{header}</tr></thead>
  <tbody>
    {row("영업현금흐름(OCF)", "operating_cf")}
    {row("투자현금흐름", "investing_cf")}
    {row("재무현금흐름", "financing_cf")}
    {row("CAPEX", "capex")}
    {row("FCF", "fcf")}
  </tbody>
</table>
</div>
"""


def _render_a4_peers(peers: list) -> str:
    if not peers:
        return ""

    rows = ""
    for p in peers:
        name = p.get("name", "")
        mktcap = p.get("market_cap", "-")
        fwd_per = p.get("fwd_per", "-")
        pbr = p.get("pbr", "-")
        ev_ebitda = p.get("ev_ebitda", "-")
        roe = p.get("roe", "-")
        opm = p.get("opm", "-")
        div_yield = p.get("div_yield", "-")

        def f(v: Any) -> str:
            try:
                return f"{float(v):.1f}"
            except (TypeError, ValueError):
                return str(v)

        rows += (
            f"<tr><td>{name}</td><td>{f(mktcap)}</td><td>{f(fwd_per)}x</td>"
            f"<td>{f(pbr)}x</td><td>{f(ev_ebitda)}x</td>"
            f"<td>{f(roe)}%</td><td>{f(opm)}%</td><td>{f(div_yield)}%</td></tr>"
        )

    return f"""
<p style="font-size:12px;font-weight:700;margin:20px 0 6px;color:var(--purple-light)">
  A-4. Peer 세부 비교 (Forward 컨센서스 / Trailing 혼용 — 기준 명시)
</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr>
      <th>기업</th><th>시총(조원)</th><th>Fwd PER</th>
      <th>PBR (Trailing)</th><th>EV/EBITDA (Fwd)</th>
      <th>ROE (%)</th><th>OPM (%)</th><th>배당수익률</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
<p style="font-size:10px;color:var(--text-sec);text-align:right;margin-top:2px">
  출처: Bloomberg, KRX, Nexus MCP. 기준일: 보고서 작성일
</p>
"""


def _render_sources(meta: dict) -> str:
    sources = meta.get("data_sources", []) or [
        "DART — 전자공시 연결재무제표 (금융감독원)",
        "KRX — 한국거래소 시세 및 공시",
        "Nexus MCP — AI 데이터 허브 (398 tools)",
        "Bloomberg Consensus — 컨센서스 추정치",
        "한국은행 ECOS — 거시경제 데이터",
    ]
    items = "".join(
        f'<li style="font-size:11px;color:var(--text-sec);margin-bottom:3px">{s}</li>'
        for s in sources
    )
    return f"""
<div style="margin:24px 0 16px;padding:14px 16px;border:1px solid var(--border);
     border-radius:2px;background:var(--surface)">
  <p style="font-size:12px;font-weight:700;margin-bottom:10px;color:var(--text)">
    Data Sources / 출처
  </p>
  <ul style="list-style:disc;margin-left:16px">{items}</ul>
</div>
"""


def _render_compliance(company: str, ticker: str, report_date: str) -> str:
    return f"""
<div style="margin-top:24px;padding:14px 16px;border:1px solid var(--border2);
     border-radius:2px;background:var(--surface2)">
  <p style="font-size:11px;font-weight:700;color:var(--text-sec);margin-bottom:8px">
    Compliance Notice
  </p>
  <p style="font-size:10px;color:var(--text-sec);line-height:1.6">
    본 보고서는 {company}({ticker})에 대한 투자 판단 참고 자료이며,
    투자 권유 목적으로 작성되지 않았습니다. 제시된 목표주가 및 추정치는
    다양한 가정에 기반하며, 실제 결과와 다를 수 있습니다. 과거 수익률은
    미래 수익률을 보장하지 않습니다. 투자 결정은 독자 본인의 판단과 책임 하에
    이루어져야 합니다. 본 보고서의 저작권은 작성자에게 있으며, 무단 복제 및
    배포를 금합니다.
    {f'<br>보고서 기준일: {report_date}' if report_date else ''}
  </p>
  <p style="font-size:10px;color:var(--text-tert);margin-top:8px;text-align:right">
    AI-Assisted Research — Luxon AI (CUFA Equity Report v16)
  </p>
</div>
"""
