"""CUFA Post-processing — Re-rating Note v2 블록 생성기.

Phase 0 Pre-flight 에서 `F2_VOLATILITY` 또는 `F1_SIGN_FLIP` 이 감지되면
v1 분석을 보존한 채 v2 재평가 블록을 **커버 직후** 삽입한다.
SKILL.md §9.3 구현체.

원칙 (v2 디자인):
1. v1 삭제 금지 — 복기 가능성을 위해 원본 분석 그대로 유지
2. v2 블록은 커버 페이지 **바로 다음**에 삽입 → 독자가 먼저 본다
3. v1/v2 수치 비교 표 필수 (TP, 상승여력, 주요 가정 변경점)
4. 새 IP, 확대된 Bear Case, 재정의된 Kill Conditions 포함
5. "v1 분석은 아래 섹션 2+ 에 보존되어 있음" 명시
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RatingChange:
    """v1 → v2 평가 변화 1건."""

    label: str                # "투자의견", "목표주가", "상승여력"
    v1_value: str             # "BUY"
    v2_value: str             # "HOLD"
    reason: str = ""          # 변화 근거 (1~2 문장)


@dataclass(frozen=True)
class ReratingNoteV2:
    """Re-rating Note v2 블록 데이터."""

    fail_code: str                           # "F2_VOLATILITY" 등
    trigger_summary: str                     # "주가 +370% 급등"
    changes: Sequence[RatingChange]          # 수치 변화 리스트
    new_investment_points: Sequence[str]     # 새 IP bullet 리스트
    new_bear_cases: Sequence[str]            # 확대된 Bear Case
    new_kill_conditions: Sequence[str]       # 재정의된 Kill condition
    v1_preserved_note: str = (
        "v1 분석은 본 보고서 섹션 2 이하에 원본 그대로 보존되어 있으며, "
        "본 블록은 복기 가능성을 위해 삭제하지 않는다."
    )


def gen_rerating_note_v2(note: ReratingNoteV2) -> str:
    """Re-rating Note v2 HTML 블록을 생성.

    커버 직후 삽입하도록 `id="rerating_v2"` 를 부여 — 이 id는
    `post_processing.protect_replace` 의 보호 영역으로 등록되어 있어
    이후 치환 규칙에서 자동으로 제외된다.
    """
    parts: list[str] = [
        '<div class="section" id="rerating_v2">',
        '<div class="section-header">',
        '  <div class="section-num" style="background:var(--amber);">!</div>',
        f'  <div class="section-title">Re-rating Note v2 — {note.fail_code}</div>',
        '</div>',
        '<div class="callout" style="border-left-color:var(--amber);'
        'background:rgba(255,217,61,0.08);">',
        f'<p><strong>트리거:</strong> {note.trigger_summary}</p>',
        '</div>',
    ]

    # v1 vs v2 비교 표
    parts.append(
        '<h3 style="margin-top:16px;">v1 vs v2 변화</h3>'
        '<div class="table-scroll"><table class="data"><thead><tr>'
        '<th>항목</th><th>v1 (원본)</th><th>v2 (재평가)</th><th>근거</th>'
        '</tr></thead><tbody>'
    )
    for ch in note.changes:
        parts.append(
            f'<tr><td>{ch.label}</td>'
            f'<td>{ch.v1_value}</td>'
            f'<td style="color:var(--amber);font-weight:600;">{ch.v2_value}</td>'
            f'<td>{ch.reason}</td></tr>'
        )
    parts.append('</tbody></table></div>')

    # 새 투자포인트
    if note.new_investment_points:
        parts.append('<h3 style="margin-top:16px;">새 투자포인트 (v2)</h3><ul>')
        parts.extend(f'<li>{ip}</li>' for ip in note.new_investment_points)
        parts.append('</ul>')

    # 확대된 Bear Case
    if note.new_bear_cases:
        parts.append(
            '<h3 style="margin-top:16px;color:var(--negative);">'
            '확대된 Bear Case</h3><ul>'
        )
        parts.extend(f'<li>{bc}</li>' for bc in note.new_bear_cases)
        parts.append('</ul>')

    # 재정의된 Kill Conditions
    if note.new_kill_conditions:
        parts.append(
            '<h3 style="margin-top:16px;color:var(--purple);">'
            '재정의된 Kill Conditions</h3><ul>'
        )
        parts.extend(f'<li>{kc}</li>' for kc in note.new_kill_conditions)
        parts.append('</ul>')

    # v1 보존 안내
    parts.append(
        f'<p style="margin-top:16px;font-size:11px;color:var(--text-sec);'
        f'font-style:italic;">※ {note.v1_preserved_note}</p>'
    )
    parts.append('</div>')
    return "\n".join(parts) + "\n"
