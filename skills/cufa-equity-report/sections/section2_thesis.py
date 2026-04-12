"""§2 3축 통합 Thesis — 투자 핵심 논거 3개 축.

HF 구조 섹션 2. 각 축에 대해 주장·근거·반증 조건을 명시한다.
falsifiable 조건이 없으면 투자 논거가 아니라 이야기에 불과하다.

포함 요소:
- 3개 투자 축 (thesis_box)
- 각 축: 상세 논거 + 핵심 데이터 포인트 + falsifiable 반증 조건
- counter-arg 블록 (Bulls vs Bears 구조)
"""
from __future__ import annotations

from typing import Any


def build_section(config: Any, html_content: str = "") -> str:
    """§2 3축 통합 Thesis 섹션 HTML 생성.

    Args:
        config: StockConfig (v16). THESIS 리스트 포함.
        html_content: 추가 본문 HTML (선택).

    Returns:
        HTML 문자열.
    """
    meta = getattr(config, "META", {}) or {}
    thesis_list = getattr(config, "THESIS", []) or []

    company = meta.get("company_name", meta.get("name", ""))
    ticker = meta.get("ticker", "")

    axes_html = _render_axes(thesis_list)

    body = html_content or ""

    return f"""
<section class="section" id="s2_thesis">
  <div class="section-header">
    <div class="section-num">2</div>
    <div class="section-title">3축 통합 Thesis — {company}</div>
    <div style="font-size:11px;color:var(--text-sec);margin-left:auto">{ticker}</div>
  </div>

  <p style="font-size:12px;color:var(--text-sec);margin-bottom:16px">
    투자 핵심 논거를 3개 축으로 압축한다. 각 축은 <strong>falsifiable</strong> 반증 조건을 명시해야 하며,
    해당 조건이 현실화될 경우 포지션을 즉시 재검토한다.
  </p>

  {axes_html}
  {body}
</section>
"""


def _render_axes(thesis_list: list) -> str:
    if not thesis_list:
        return '<p style="color:var(--text-sec)">THESIS 데이터 없음.</p>'

    parts: list[str] = ['<div class="thesis-box" style="display:flex;flex-direction:column;gap:16px">']

    for i, ax in enumerate(thesis_list[:3], 1):
        if not isinstance(ax, dict):
            ax = {"title": str(ax)}

        title = ax.get("title", "")
        detail = ax.get("detail", "")
        data_points = ax.get("data_points", []) or []
        falsifiable = ax.get("falsifiable", "")

        dp_html = ""
        if data_points:
            items = "".join(
                f'<li style="font-size:11px;color:var(--text-sec);margin-bottom:3px">{dp}</li>'
                for dp in data_points
            )
            dp_html = f'<ul style="margin:6px 0 0 14px;list-style:disc">{items}</ul>'

        falsifiable_html = ""
        if falsifiable:
            falsifiable_html = f"""
    <div class="counter-arg" style="margin-top:10px">
      <div style="font-size:10px;font-weight:700;color:var(--negative);margin-bottom:4px">
        이 가정이 틀리면 (falsifiable 반증 조건)
      </div>
      <p style="font-size:11px;color:var(--text)">{falsifiable}</p>
    </div>"""

        parts.append(f"""
  <div style="border:1px solid var(--border);border-left:3px solid var(--purple);
              padding:14px 16px;border-radius:2px;background:var(--surface)">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
      <div style="background:var(--purple);color:#fff;width:24px;height:24px;border-radius:50%;
                  display:flex;align-items:center;justify-content:center;font-weight:700;
                  font-size:12px;flex-shrink:0">{i}</div>
      <div style="font-size:14px;font-weight:700;color:var(--text)">{title}</div>
    </div>
    <p style="font-size:12px;line-height:1.6;color:var(--text-sec)">{detail}</p>
    {dp_html}
    {falsifiable_html}
  </div>""")

    parts.append("</div>")
    return "\n".join(parts)
