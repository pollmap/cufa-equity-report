"""
Phase 7 Feedback Loop — CUFA Equity Report v16

Compares CUFA estimates (from TradeTicket) vs actual outcomes (from BacktestResult
or manual entry) and generates a structured revision report.

This is the "복기" (post-mortem) engine. Every report is an experiment;
Phase 7 measures what was right, what was wrong, and why.

Output:
    - FeedbackReport (structured)
    - Markdown summary saved to data/feedback/{ticker}_{date}_feedback.md
    - Adjustable parameters fed back into next report's StockConfig

Usage:
    from trade_ticket.feedback import run_feedback_loop
    report = run_feedback_loop(ticket, backtest_result, notes="LNG 수요 예측 오버슈팅")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .backtest_hook import BacktestResult
from .schema import TradeTicket, TradeOpinion


# ---------------------------------------------------------------------------
# Deviation Classification
# ---------------------------------------------------------------------------

DEVIATION_THRESHOLDS = {
    "excellent":  (-0.05, 0.05),    # ±5% — within noise
    "acceptable": (-0.15, 0.15),    # ±15% — reasonable estimate
    "review":     (-0.30, 0.30),    # ±30% — need to revise assumptions
    "major_miss": None,             # outside ±30% — full thesis review
}


def _classify_deviation(dev_pct: float) -> str:
    abs_dev = abs(dev_pct) / 100
    if abs_dev <= 0.05:
        return "excellent"
    if abs_dev <= 0.15:
        return "acceptable"
    if abs_dev <= 0.30:
        return "review"
    return "major_miss"


# ---------------------------------------------------------------------------
# Feedback Report Schema
# ---------------------------------------------------------------------------

@dataclass
class AssumptionDelta:
    """One changed assumption between report estimate and actual."""
    field: str              # e.g. "revenue_growth_2025E"
    estimated: Any
    actual: Any
    delta_pct: float | None = None
    root_cause: str = ""    # e.g. "LNG 발주 지연", "환율 급변"


@dataclass
class FeedbackReport:
    ticker: str
    company_name: str
    report_date: str            # original report date
    review_date: str            # today
    horizon_months: int

    # Core metrics
    estimated_return_pct: float     # (TP - Entry) / Entry
    realized_return_pct: float
    deviation_pct: float            # actual - estimated
    deviation_class: str            # excellent / acceptable / review / major_miss

    # Kill condition tracking
    kill_triggered: str | None = None
    kill_missed: list[str] = field(default_factory=list)

    # Assumption deltas
    assumption_deltas: list[AssumptionDelta] = field(default_factory=list)

    # Qualitative assessment
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    analyst_notes: str = ""

    # Next-report adjustments (fed back into config)
    param_adjustments: dict[str, Any] = field(default_factory=dict)

    # Performance stats
    hit_stop: bool = False
    hit_target: bool = False
    max_drawdown_pct: float = 0.0


# ---------------------------------------------------------------------------
# Core Function
# ---------------------------------------------------------------------------

def run_feedback_loop(
    ticket: TradeTicket,
    result: BacktestResult,
    analyst_notes: str = "",
    assumption_deltas: list[AssumptionDelta] | None = None,
    output_dir: Path | None = None,
) -> FeedbackReport:
    """
    Compare TradeTicket estimates vs BacktestResult actuals.
    Generate a FeedbackReport and save the markdown summary.

    Args:
        ticket:           Original TradeTicket from report.
        result:           BacktestResult from backtest_hook.py.
        analyst_notes:    Free-text notes from analyst (what happened?).
        assumption_deltas: List of changed assumptions with root causes.
        output_dir:       Where to save the markdown. Defaults to data/feedback/.

    Returns:
        FeedbackReport
    """
    # Estimated return
    if ticket.entry_price > 0:
        estimated_return_pct = round(
            (ticket.target_price - ticket.entry_price) / ticket.entry_price * 100, 2
        )
    else:
        estimated_return_pct = 0.0

    deviation_pct = result.realized_return_pct - estimated_return_pct
    deviation_class = _classify_deviation(deviation_pct)

    # Auto-detect kill condition misses
    kill_missed = []
    if not result.hit_kill and result.hit_stop:
        kill_missed = ["손절가 도달 — 사전 Kill Condition 미탐지"]

    report = FeedbackReport(
        ticker=ticket.ticker,
        company_name=ticket.company_name,
        report_date=ticket.generated_at,
        review_date=date.today().isoformat(),
        horizon_months=ticket.horizon_months,
        estimated_return_pct=estimated_return_pct,
        realized_return_pct=result.realized_return_pct,
        deviation_pct=round(deviation_pct, 2),
        deviation_class=deviation_class,
        kill_triggered=result.hit_kill,
        kill_missed=kill_missed,
        assumption_deltas=assumption_deltas or [],
        analyst_notes=analyst_notes,
        param_adjustments=_compute_param_adjustments(deviation_pct, result),
        hit_stop=result.hit_stop,
        hit_target=result.hit_target,
        max_drawdown_pct=result.max_drawdown_pct,
    )

    # Persist
    if output_dir is None:
        output_dir = Path.cwd() / "data" / "feedback"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{ticket.ticker}_{date.today().isoformat()}_feedback.md"
    _write_feedback_md(report, md_path)
    print(f"[feedback] Phase 7 복기 저장: {md_path}")

    return report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_param_adjustments(
    deviation_pct: float, result: BacktestResult
) -> dict[str, Any]:
    """
    Suggest parameter adjustments for the next report based on deviation.
    These are soft suggestions — analyst must confirm before applying.
    """
    adjustments: dict[str, Any] = {}
    abs_dev = abs(deviation_pct)

    if abs_dev > 30:
        adjustments["conviction"] = "HIGH → MEDIUM (major miss, review thesis)"
        adjustments["position_size_pct"] = "reduce by 1~2%"
    elif abs_dev > 15:
        adjustments["stop_loss"] = "tighten by 5%"
    elif abs_dev < 5:
        adjustments["conviction"] = "confirm — estimate was accurate"

    if result.hit_stop:
        adjustments["kill_conditions"] = "add 1 more leading indicator"

    return adjustments


def _write_feedback_md(report: FeedbackReport, path: Path) -> None:
    """Write a structured markdown Phase 7 복기 report."""
    icon_map = {
        "excellent": "✅",
        "acceptable": "🟡",
        "review": "🟠",
        "major_miss": "🔴",
    }
    icon = icon_map.get(report.deviation_class, "⚪")

    lines = [
        f"# Phase 7 복기 — {report.company_name} ({report.ticker})",
        f"> 보고서 작성: {report.report_date} | 복기 일자: {report.review_date}",
        "",
        "## 핵심 성과 요약",
        "",
        f"| 항목 | 추정 | 실제 | 편차 |",
        f"|---|---:|---:|---:|",
        f"| 수익률 | {report.estimated_return_pct:+.1f}% | {report.realized_return_pct:+.1f}% | {report.deviation_pct:+.1f}% |",
        f"| MDD | - | {report.max_drawdown_pct:.1f}% | - |",
        "",
        f"**편차 등급**: {icon} {report.deviation_class.upper()}",
        "",
    ]

    if report.kill_triggered:
        lines += [
            "## Kill Condition 발동",
            f"- **발동**: {report.kill_triggered}",
            "",
        ]

    if report.kill_missed:
        lines += ["## 놓친 Kill Condition"]
        for k in report.kill_missed:
            lines.append(f"- {k}")
        lines.append("")

    if report.assumption_deltas:
        lines += [
            "## 가정 편차 분석",
            "",
            "| 항목 | 추정 | 실제 | 원인 |",
            "|---|---|---|---|",
        ]
        for delta in report.assumption_deltas:
            dp = f"{delta.delta_pct:+.1f}%" if delta.delta_pct is not None else "-"
            lines.append(
                f"| {delta.field} | {delta.estimated} | {delta.actual} ({dp}) | {delta.root_cause} |"
            )
        lines.append("")

    if report.param_adjustments:
        lines += ["## 다음 보고서 파라미터 조정 제안", ""]
        for k, v in report.param_adjustments.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")

    if report.analyst_notes:
        lines += [
            "## 애널리스트 메모",
            "",
            report.analyst_notes,
            "",
        ]

    lines += [
        "---",
        f"*CUFA Equity Report v16 — Phase 7 자동 생성 | {report.review_date}*",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
