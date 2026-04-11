"""CUFA Builder — 본문 컴포넌트 헬퍼.

SMIC 패턴(counter_arg, chart_with_context)과 CUFA 고유 컴포넌트
(expand_card, proprietary_metric, valuation_rationale)를 모은다.
모두 순수 함수로, 입력 → HTML 문자열 반환.
"""
from __future__ import annotations

import hashlib
from typing import Iterable


def expand_card(title: str, meta: str, content: str) -> str:
    """클릭으로 펼쳐지는 카드. 상세 정보 접기/펼치기 UI."""
    card_id = "ec_" + hashlib.md5(title.encode()).hexdigest()[:8]
    return (
        f'<div class="expand-card" id="{card_id}" '
        f'onclick="this.classList.toggle(\'open\')">\n'
        f'<div class="expand-header">\n'
        f'  <div><h4>{title}</h4><div class="expand-meta">{meta}</div></div>\n'
        f'  <span class="expand-arrow">\u25b6</span>\n'
        f'</div>\n'
        f'<div class="expand-body"><div class="expand-content">\n'
        f'{content}\n'
        f'</div></div>\n'
        f'</div>\n'
    )


def counter_arg(concern: str, rebuttal: str) -> str:
    """시장의 우려 → 반박 2단 블록. SMIC 패턴. IP당 최소 1개 필수."""
    return (
        f'<div class="counter-arg">\n'
        f'<p class="concern-label">시장의 우려</p>\n'
        f'<p style="font-size:13px;color:var(--text-sec);'
        f'margin-bottom:10px;">{concern}</p>\n'
        f'<p class="rebuttal-label">반박</p>\n'
        f'<p style="font-size:13px;color:var(--text);margin:0;">{rebuttal}</p>\n'
        f'</div>\n'
    )


def add_source(chart_html: str, src: str = "DART, CUFA") -> str:
    """차트 HTML 마지막 `</div>\\n` 앞에 출처 `<p>` 삽입.

    멱등 보장 없음 — 같은 차트에 두 번 호출하면 두 개 삽입된다.
    출처율 95% 규칙을 만족시키기 위해 모든 차트/테이블에 1회 호출 권장.
    """
    idx = chart_html.rfind("</div>\n")
    if idx < 0:
        return chart_html
    tail = (
        f'<p style="font-size:10px;color:var(--text-sec);'
        f'text-align:right;margin-top:4px;">출처: {src}</p></div>\n'
    )
    return chart_html[:idx] + tail


def chart_with_context(pre_text: str, chart_html: str, post_text: str) -> str:
    """차트 전후에 해설 문단을 강제 삽입 (SMIC 패턴).

    SMIC 보고서의 핵심 패턴: 차트는 단독으로 서 있지 않고,
    반드시 앞에 맥락 문장, 뒤에 해석 문장이 붙는다.
    """
    pre = (
        f'<p style="font-size:12px;line-height:1.5;color:var(--text);'
        f'margin-bottom:6px;">{pre_text}</p>\n'
    )
    post = (
        f'<p style="font-size:12px;line-height:1.5;color:var(--text);'
        f'margin:6px 0;">{post_text}</p>\n'
    )
    return pre + chart_html + post


def data_tip(text: str, tip: str) -> str:
    """마우스 호버 시 상세 설명 팝업. 본문 인라인 용어 설명용."""
    return (
        f'<span class="data-tip" title="{tip}" '
        f'style="border-bottom:1px dotted var(--purple);cursor:help;">{text}</span>'
    )


def scenario_tabs(bull_html: str, base_html: str, bear_html: str) -> str:
    """Bull / Base / Bear 3개 시나리오 카드 그리드."""
    return (
        f'<div class="scenario-grid">\n'
        f'<div class="scenario-card bull">{bull_html}</div>\n'
        f'<div class="scenario-card base">{base_html}</div>\n'
        f'<div class="scenario-card bear">{bear_html}</div>\n'
        f'</div>\n'
    )


def proprietary_metric(
    name: str,
    formula: str,
    description: str,
    tracking: str,
    viz_html: str = "",
) -> str:
    """CUFA 독자 분석 프레임 블록.

    Args:
        name: 프레임 이름 (예: "Kitchen Sinking Index")
        formula: 산식 (예: "OCF / Net Income")
        description: 의미·해석 설명
        tracking: 모니터링 방법 (분기별/월별/이벤트)
        viz_html: 선택 시각화 HTML (차트 등)
    """
    return (
        f'<div style="background:var(--purple-bg);border:1px solid var(--purple-border);'
        f'padding:20px;margin:20px 0;border-radius:var(--border-radius);">\n'
        f'<p style="color:var(--purple-light);font-size:16px;'
        f'font-weight:700;margin-bottom:8px;">{name}</p>\n'
        f'<p style="color:var(--text);font-size:13px;margin:4px 0;">'
        f'<strong>산식:</strong> {formula}</p>\n'
        f'<p style="color:var(--text);font-size:13px;line-height:1.7;'
        f'margin:8px 0;">{description}</p>\n'
        f'<p style="color:var(--text-sec);font-size:12px;">'
        f'<strong>추적:</strong> {tracking}</p>\n'
        f'{viz_html}\n'
        f'</div>\n'
    )


def valuation_rationale(
    chosen: str,
    chosen_reason: str,
    excluded_list: Iterable[tuple[str, str]],
) -> str:
    """밸류에이션 방법론 선택/배제 근거 블록.

    Args:
        chosen: 선택한 방법 (예: "PBR Method")
        chosen_reason: 왜 선택했는지 2~3문장
        excluded_list: `[(방법, 배제사유), ...]` 튜플 시퀀스
    """
    parts: list[str] = [
        '<div style="background:rgba(124,106,247,0.05);'
        'border-left:3px solid var(--purple);padding:16px;margin:20px 0;'
        'border-radius:0 4px 4px 0;">',
        f'<p style="color:var(--purple-light);font-size:14px;'
        f'font-weight:700;margin-bottom:8px;">선택 방법론: {chosen}</p>',
        f'<p style="color:var(--text);font-size:13px;line-height:1.7;'
        f'margin-bottom:12px;">{chosen_reason}</p>',
        '<div style="border-top:1px solid var(--border);padding-top:12px;">',
    ]
    for method, reason in excluded_list:
        parts.append(
            f'<p style="color:var(--text-sec);font-size:13px;margin:4px 0;">'
            f'\u2715 <strong>{method}</strong> 부적합: {reason}</p>'
        )
    parts.append("</div></div>")
    return "\n".join(parts) + "\n"


def implied_per_check(
    target_price: float,
    terminal_eps: float,
    terminal_year: int,
) -> str:
    """Implied PER Sanity Check 블록.

    목표주가가 터미널 EPS 대비 합리적 범위(<30x)인지 자동 판정.
    30x 미만=합리적(positive), 40x 미만=공격적, 40x+=Red Flag(negative).
    """
    if terminal_eps <= 0:
        implied = float("inf")
        flag, color = "EPS 음수", "var(--text-sec)"
    else:
        implied = target_price / terminal_eps
        if implied < 30:
            flag, color = "합리적", "var(--positive)"
        elif implied < 40:
            flag, color = "공격적", "var(--amber)"
        else:
            flag, color = "Red Flag", "var(--negative)"
    implied_txt = f"{implied:.1f}x" if implied != float("inf") else "N/A"
    return (
        f'<div style="background:var(--surface2);padding:12px 16px;'
        f'margin:12px 0;border-radius:var(--border-radius);">\n'
        f'<p style="font-size:13px;color:var(--text-sec);">'
        f'Implied PER Sanity Check ({terminal_year}E)</p>\n'
        f'<p style="font-size:15px;color:var(--text);font-weight:600;">\n'
        f'  목표주가 {target_price:,.0f}원 \u00f7 '
        f'{terminal_year}E EPS {terminal_eps:,.0f}원 = '
        f'<span style="color:{color};">{implied_txt}</span> ({flag})\n'
        f'</p></div>\n'
    )
