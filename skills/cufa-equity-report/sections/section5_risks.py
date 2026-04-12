"""§5 Risks — Bear Case First.

HF 구조 섹션 5. 낙관적 프레이밍 금지. Bear Case를 먼저 제시한다.
투자 논거가 붕괴되는 조건(Kill Condition)을 명시한다.

포함 요소:
- Bear Case 시나리오 요약 (먼저)
- Kill Condition 테이블
- EPS 민감도 테이블
- 리스크 매트릭스 (확률 × 영향도)
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§5 Risks 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). kill_conditions / KILL_CONDITIONS, RISK_MATRIX 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    # 소문자/대문자 둘 다 허용
    kill_raw = getattr(config, "kill_conditions", None) or getattr(config, "KILL_CONDITIONS", []) or []
    scenarios = getattr(config, "VALUATION_SCENARIOS", {}) or {}
    risk_matrix = getattr(config, "RISK_MATRIX", []) or []
    eps_sensitivity = getattr(config, "EPS_SENSITIVITY", []) or []

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")

    bear_html = _render_bear_first(scenarios)
    kill_html = _render_kill_conditions(kill_raw)
    eps_html = _render_eps_sensitivity(eps_sensitivity)
    matrix_html = _render_risk_matrix(risk_matrix)

    body = html_content or ""

    return f"""
<section class="section" id="s5_risks">
  <div class="section-header">
    <div class="section-num">5</div>
    <div class="section-title">Risks — Bear Case First — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  <div class="callout" style="border-left:3px solid var(--negative);background:var(--surface);
       padding:10px 16px;margin-bottom:16px;border-radius:2px">
    <p style="font-size:11px;color:var(--negative);font-weight:700">
      Bear Case를 먼저 읽어라. 최악의 시나리오를 감내할 수 있을 때만 포지션을 잡는다.
    </p>
  </div>

  {bear_html}
  {kill_html}
  {eps_html}
  {matrix_html}
  {body}
</section>
"""


def _render_bear_first(scenarios: dict) -> str:
    bear = scenarios.get("bear", {}) or {}
    base = scenarios.get("base", {}) or {}
    bull = scenarios.get("bull", {}) or {}

    if not (bear or base or bull):
        return '<p style="color:var(--text-sec);margin-bottom:16px">VALUATION_SCENARIOS 데이터 없음.</p>'

    def card(label: str, d: dict, color: str) -> str:
        price = d.get("price", 0)
        prob = d.get("probability_pct", d.get("prob_pct", ""))
        desc = d.get("description", d.get("desc", ""))
        try:
            price_str = f"{int(price):,}원"
        except (TypeError, ValueError):
            price_str = str(price)
        prob_str = f"확률 {prob}%" if prob else ""
        return f"""
<div class="scenario-card {label.lower()}" style="flex:1;padding:14px;border:1px solid var(--border);
     border-top:3px solid {color};border-radius:2px;background:var(--surface)">
  <div style="font-size:11px;font-weight:700;color:{color};margin-bottom:6px">{label}</div>
  <div style="font-size:20px;font-weight:700;color:var(--text);margin-bottom:4px">{price_str}</div>
  <div style="font-size:10px;color:var(--text-sec);margin-bottom:6px">{prob_str}</div>
  <p style="font-size:11px;color:var(--text-sec);line-height:1.5">{desc}</p>
</div>"""

    # Bear를 맨 앞에
    return f"""
<p style="font-size:13px;font-weight:700;margin:0 0 10px">시나리오 가격 (Bear First)</p>
<div style="display:flex;gap:12px;margin-bottom:20px">
  {card("Bear", bear, "var(--negative)")}
  {card("Base", base, "var(--amber)")}
  {card("Bull", bull, "var(--positive)")}
</div>
"""


def _render_kill_conditions(kill_raw: list) -> str:
    if not kill_raw:
        return f"""
<div style="margin:16px 0;padding:12px 16px;border:1px solid var(--negative);
     border-radius:2px;background:var(--surface)">
  <p style="font-size:12px;font-weight:700;color:var(--negative);margin-bottom:4px">
    Kill Condition — 포지션 청산 트리거
  </p>
  <p style="font-size:11px;color:var(--text-sec)">
    kill_conditions 리스트를 설정하세요. (예: [{{"id":"kill_01","condition":"...",
    "action":"즉시 전량 청산"}}])
  </p>
</div>
"""

    rows = ""
    for kc in kill_raw:
        kid = kc.get("id", "kill_")
        cond = kc.get("condition", "")
        action = kc.get("action", "즉시 청산")
        rows += (
            f'<tr><td style="font-size:10px;color:var(--amber);font-weight:600">{kid}</td>'
            f"<td>{cond}</td>"
            f'<td style="color:var(--negative);font-weight:600">{action}</td></tr>'
        )

    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px;color:var(--negative)">
  Kill Condition — 투자 논거 붕괴 조건
</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr><th>ID</th><th>청산 조건</th><th>대응 액션</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


def _render_eps_sensitivity(eps_sens: list) -> str:
    if not eps_sens:
        return ""

    rows = "".join(
        f"<tr><td>{s.get('variable','')}</td><td>{s.get('base_assumption','')}</td>"
        f"<td>{s.get('change','')}</td><td>{s.get('eps_impact','')}</td></tr>"
        for s in eps_sens
    )
    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px">EPS 민감도 분석</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr><th>변수</th><th>기준 가정</th><th>변화폭</th><th>EPS 영향</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""


def _render_risk_matrix(risk_matrix: list) -> str:
    if not risk_matrix:
        return ""

    def color(prob: Any, impact: Any) -> str:
        try:
            score = float(str(prob).replace("%", "")) * float(str(impact).replace("%", ""))
            if score >= 1500:
                return "var(--negative)"
            if score >= 600:
                return "var(--amber)"
            return "var(--text-sec)"
        except (TypeError, ValueError):
            return "var(--text-sec)"

    rows = ""
    for r in risk_matrix:
        label = r.get("risk", r.get("label", ""))
        prob = r.get("probability", r.get("prob", ""))
        impact = r.get("impact", "")
        mitigation = r.get("mitigation", r.get("comment", ""))
        c = color(prob, impact)
        rows += (
            f'<tr><td style="color:{c};font-weight:600">{label}</td>'
            f"<td>{prob}</td><td>{impact}</td><td>{mitigation}</td></tr>"
        )

    return f"""
<p style="font-size:13px;font-weight:700;margin:20px 0 8px">리스크 매트릭스 (확률 × 영향도)</p>
<div class="table-scroll">
<table class="data">
  <thead>
    <tr><th>리스크 항목</th><th>발생 확률</th><th>영향도</th><th>대응 방안</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>
"""
