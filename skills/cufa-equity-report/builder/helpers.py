"""CUFA Builder — 레이아웃·테이블 헬퍼.

section_header, sidebar_wrap, table, backtest_result_table 등
"구조 틀"에 해당하는 빌딩 블록을 모은다.
"""
from __future__ import annotations

import html as _html
from typing import Iterable, Sequence

from .figure import fig_num


def section_header(
    num: int,
    title: str,
    company_name: str,
    ticker: str,
) -> str:
    """섹션 헤더 + 러닝 헤더 + 섹션 번호 뱃지.

    섹션 div를 연다. 짝이 되는 `</div>` 는 호출자가 닫아야 한다.
    """
    return (
        f'\n<div class="section" id="sec{num}">\n'
        f'  <div class="section-subheader">'
        f'Equity Research Report | {company_name} ({ticker})</div>\n'
        f'  <div class="section-header">\n'
        f'    <div class="section-num">{num}</div>\n'
        f'    <div class="section-title">{title}</div>\n'
        f'  </div>\n'
    )


def sidebar_wrap(
    keywords: Sequence[tuple[str, str]],
    content: str,
) -> str:
    """SMIC 2열 레이아웃 (좌 사이드 키워드 / 우 본문).

    Args:
        keywords: `[(헤드, 해석문), ...]` — 소제목형/포인트형/주의형 모두 가능.
                  길이 3~15자 권장. 15자 초과 시 자동 줄바꿈.
        content: 본문 HTML. 차트/테이블/단락 섞어도 무방.

    사이드바 안쪽에는 절대 차트/테이블 넣지 않는다 (feedback_sidebar_strict).
    """
    parts = ['<div class="sidebar-layout">', '<div class="sidebar-kw">']
    for head, val in keywords:
        parts.append(f'  <div class="kw">{head}</div><div class="kw-val">{val}</div>')
    parts += ['</div>', '<div class="content-area">', content, '</div>', '</div>']
    return "\n".join(parts) + "\n"


def table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str | int | float]],
    highlight_rows: Iterable[int] | None = None,
    sec: int = 0,
    title: str = "",
    src: str = "",
) -> str:
    """데이터 테이블. `table.data` CSS 클래스 적용.

    Args:
        headers: 컬럼 헤더
        rows: 2차원 셀 배열
        highlight_rows: 강조할 행 인덱스 집합
        sec: 섹션 번호 (도표 번호 부여용; 0이면 미부여)
        title: 테이블 타이틀 (제공되면 상단 레이블 출력)
        src: 출처 표기 (제공되면 하단 레이블 출력)
    """
    highlight = set(highlight_rows or ())
    out: list[str] = []
    if title:
        ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
        out.append(
            f'<p style="font-size:12px;color:var(--text-sec);'
            f'margin:12px 0 6px;font-weight:600;">{ftitle}</p>'
        )
    out.append('<table class="data"><tr>')
    out += [f"<th>{h}</th>" for h in headers]
    out.append("</tr>")
    for i, row in enumerate(rows):
        cls = ' class="highlight-row"' if i in highlight else ""
        out.append(f"<tr{cls}>")
        out += [f"<td>{cell}</td>" for cell in row]
        out.append("</tr>")
    out.append("</table>")
    if src:
        out.append(
            f'<p style="font-size:10px;color:var(--text-sec);'
            f'text-align:right;margin-top:2px;">출처: {src}</p>'
        )
    return "\n".join(out) + "\n"


def backtest_result_table(results: Sequence[dict], sec: int = 0) -> str:
    """Phase 6.5 백테스트 결과를 HTML 테이블로 렌더.

    Args:
        results: `[{"strategy": "SMA", "total_return": 18.3,
                    "max_drawdown": -12.4, "sharpe_ratio": 1.42,
                    "win_rate": 58.3}, ...]`
        sec: 섹션 번호 (도표 번호 부여용)
    """
    ftitle = f"도표 {fig_num(sec)}. 백테스트 전략 비교" if sec else "백테스트 전략 비교"
    parts: list[str] = [
        f'<div class="chart-box"><div class="chart-title">{ftitle}</div>',
        '<div class="table-scroll"><table class="data"><thead><tr>',
        "<th>전략</th><th>수익률</th><th>MDD</th>"
        "<th>샤프비율</th><th>승률</th>",
        "</tr></thead><tbody>",
    ]
    for r in results:
        total = r.get("total_return", 0.0)
        mdd = r.get("max_drawdown", 0.0)
        sharpe = r.get("sharpe_ratio", 0.0)
        win = r.get("win_rate", 0.0)
        ret_color = "var(--positive)" if total >= 0 else "var(--negative)"
        mdd_color = "var(--negative)" if mdd < -15 else "var(--text-sec)"
        strategy = _html.escape(str(r.get("strategy", "")))
        parts.append(
            f"<tr><td>{strategy}</td>"
            f'<td style="color:{ret_color}">{total:+.1f}%</td>'
            f'<td style="color:{mdd_color}">{mdd:.1f}%</td>'
            f"<td>{sharpe:.2f}</td>"
            f"<td>{win:.1f}%</td></tr>"
        )
    parts += [
        "</tbody></table></div>",
        '<p style="font-size:11px;color:var(--text-sec);margin-top:6px;">'
        "\u203b 백테스트 결과는 과거 데이터 기반이며 미래 수익을 보장하지 않습니다. "
        "수수료 0.015%, 거래세 0.2% 반영.</p>",
        "</div>",
    ]
    return "\n".join(parts) + "\n"
