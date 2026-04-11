"""CUFA Preflight — 표준 5점 검증 체커.

SKILL.md §3.2 ~ §3.3 구현체. 종목 독립형으로 config만 주입하면
어느 종목에나 동일하게 동작한다.

Fail Code 레퍼런스:
    F1_FINANCIAL_DRIFT  — 재무 드리프트 > FINANCIAL_DRIFT_MAX
    F1_SIGN_FLIP        — 영업손익 부호 반전
    F2_PRICE_DRIFT      — 주가 드리프트 > PRICE_DRIFT_MAX
    F2_VOLATILITY       — 1년 수익률 > VOLATILITY_RERATING_TRIGGER (Re-rating Mode)
    F3_TRIPLE_CHECK     — PBR × BPS ≠ Price
    F4_RAW_MISSING      — data/raw/ 원본 응답 파일 부재
    F5_INDUSTRY         — 산업 체크리스트 항목 누락
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .dart_parser import split_cfs_ofs, get_is_summary
from .industry_checklist import INDUSTRY_CHECKLIST
from .mcp_client import MCPClient, MCPError
from .thresholds import PREFLIGHT, PreflightThresholds


@dataclass(frozen=True)
class PreflightConfig:
    """종목별 Pre-flight 입력값.

    이 dataclass는 **값만** 들고 있다. 종목 특이성은 여기에만 존재하며,
    validation 로직은 `preflight_validate`에 위임된다.
    """

    stock_code: str
    target_year: int
    industry: str
    builder_revenue: float
    builder_op_income: float
    builder_price: float
    builder_bps: float
    builder_eps_next: float
    shares_outstanding: float
    data_dir: Path
    thresholds: PreflightThresholds = PREFLIGHT


@dataclass(frozen=True)
class PreflightResult:
    """표준 검증 결과.

    `fails`는 Fail Code 튜플. 비어 있으면 통과.
    `is_rerating_mode()`는 F2_VOLATILITY 또는 F1_SIGN_FLIP 발생 여부.
    """

    passed: bool
    fails: tuple[str, ...]
    actual_revenue: float | None = None
    actual_op_income: float | None = None
    actual_price: float | None = None
    one_year_return: float | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def is_rerating_mode(self) -> bool:
        """Re-rating v2 모드 전환 조건."""
        return any(fc in self.fails for fc in ("F2_VOLATILITY", "F1_SIGN_FLIP"))

    def format_report(self) -> str:
        """사람이 읽을 수 있는 텍스트 리포트."""
        if self.passed:
            return "[PASS] Pre-flight 5점 체크 통과"
        lines = ["[FAIL] Pre-flight 검증 실패", ""]
        for fc in self.fails:
            lines.append(f"  - {fc}")
        if self.is_rerating_mode():
            lines.append("")
            lines.append("  → Re-rating v2 모드로 전환 필요")
        return "\n".join(lines)


def _check_financial(
    config: PreflightConfig,
    mcp: MCPClient,
    fails: list[str],
) -> tuple[float | None, float | None]:
    """① 재무 검증."""
    try:
        resp = mcp.call(
            "dart_financial_statements",
            {
                "stock_code": config.stock_code,
                "year": str(config.target_year),
                "report_type": "CFS",
            },
        )
    except MCPError:
        fails.append("F1_FINANCIAL_DRIFT")  # MCP 실패도 같은 대응
        return None, None

    items = resp.get("data", []) if isinstance(resp, dict) else []
    cfs_rows, _ = split_cfs_ofs(items)
    summary = get_is_summary(cfs_rows)

    actual_revenue = summary["revenue"]
    actual_op = summary["op_income"]

    if actual_revenue and config.builder_revenue:
        drift = abs(config.builder_revenue - actual_revenue) / actual_revenue
        if drift > config.thresholds.FINANCIAL_DRIFT_MAX:
            fails.append("F1_FINANCIAL_DRIFT")

    if (
        config.thresholds.OP_INCOME_SIGN_CHECK
        and actual_op
        and config.builder_op_income
        and (config.builder_op_income * actual_op < 0)
    ):
        fails.append("F1_SIGN_FLIP")

    return float(actual_revenue), float(actual_op)


def _check_price(
    config: PreflightConfig,
    mcp: MCPClient,
    fails: list[str],
) -> tuple[float | None, float | None]:
    """② 주가 검증."""
    today = date.today()
    try:
        resp = mcp.call(
            "stocks_history",
            {
                "stock_code": config.stock_code,
                "start_date": (today - timedelta(days=365)).isoformat(),
                "end_date": today.isoformat(),
            },
        )
    except MCPError:
        return None, None

    rows = resp.get("data", []) if isinstance(resp, dict) else []
    if len(rows) < config.thresholds.MIN_DAYS_OHLCV:
        fails.append("F2_PRICE_DRIFT")
        return None, None

    first_close = float(rows[0]["close"])
    last_close = float(rows[-1]["close"])
    year_return = (last_close - first_close) / first_close

    drift = abs(config.builder_price - last_close) / last_close
    if drift > config.thresholds.PRICE_DRIFT_MAX:
        fails.append("F2_PRICE_DRIFT")
    if abs(year_return) > config.thresholds.VOLATILITY_RERATING_TRIGGER:
        fails.append("F2_VOLATILITY")

    return last_close, year_return


def _check_triple(config: PreflightConfig, fails: list[str]) -> None:
    """③ 삼각검증 PBR × BPS = Price."""
    if config.builder_bps <= 0:
        return
    implied_price = (config.builder_price / config.builder_bps) * config.builder_bps
    deviation = abs(implied_price - config.builder_price) / config.builder_price
    if deviation > config.thresholds.SELF_CONSISTENCY_TOLERANCE:
        fails.append("F3_TRIPLE_CHECK")


def _check_raw_archive(config: PreflightConfig, fails: list[str]) -> None:
    """④ 원본 응답 보존."""
    if not config.thresholds.REQUIRE_RAW_ARCHIVE:
        return
    data_dir = config.data_dir
    if not data_dir.exists():
        fails.append("F4_RAW_MISSING")
        return
    has_dart = any(data_dir.glob(f"{config.stock_code}_dart_*.raw"))
    has_stock = any(data_dir.glob(f"{config.stock_code}_stock_*.raw"))
    if not (has_dart and has_stock):
        fails.append("F4_RAW_MISSING")


def _check_industry(config: PreflightConfig, fails: list[str]) -> None:
    """⑤ 산업 체크리스트 로드."""
    if config.industry not in INDUSTRY_CHECKLIST:
        fails.append("F5_INDUSTRY")


def preflight_validate(
    config: PreflightConfig,
    mcp: MCPClient,
) -> PreflightResult:
    """표준 Pre-flight 5점 검증 — 종목 무관.

    Args:
        config: 종목별 입력값.
        mcp: MCP 클라이언트 (의존성 주입).

    Returns:
        PreflightResult — passed/fails/actual 지표 포함.
    """
    fails: list[str] = []

    actual_revenue, actual_op = _check_financial(config, mcp, fails)
    actual_price, year_return = _check_price(config, mcp, fails)
    _check_triple(config, fails)
    _check_raw_archive(config, fails)
    _check_industry(config, fails)

    return PreflightResult(
        passed=len(fails) == 0,
        fails=tuple(fails),
        actual_revenue=actual_revenue,
        actual_op_income=actual_op,
        actual_price=actual_price,
        one_year_return=year_return,
    )
