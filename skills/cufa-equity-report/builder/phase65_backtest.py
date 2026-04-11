"""CUFA Builder — Phase 6.5 백테스트 검증.

Nexus `backtest_run` MCP 도구를 래핑하여 투자포인트에서 매매 전략을
추출·실행·결과 수집한다. KIS-backtest MCP 로컬 서버가 내려가 있을 때는
Nexus fallback 으로 자동 전환.

SKILL.md §10.4 구현체.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Sequence

from preflight.mcp_client import NexusMCPClient


@dataclass(frozen=True)
class StrategySpec:
    """백테스트 전략 1건."""

    name: str                # "MA_cross", "Momentum", "Mean_reversion"
    params: dict = field(default_factory=dict)
    description: str = ""


@dataclass(frozen=True)
class BacktestResult:
    """백테스트 결과 단위 (strategy-level)."""

    strategy: str
    total_return: float      # % — 누적 수익률
    max_drawdown: float      # % — 최대 낙폭 (음수)
    sharpe_ratio: float
    win_rate: float          # % — 승률
    raw: dict = field(default_factory=dict)  # MCP 응답 원본

    def as_table_row(self) -> dict:
        """helpers.backtest_result_table() 호환 dict 반환."""
        return {
            "strategy": self.strategy,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
        }


#: 기본 3전략. 대부분 종목에 적용 가능.
DEFAULT_STRATEGIES: tuple[StrategySpec, ...] = (
    StrategySpec("MA_cross", {"short": 20, "long": 60},
                 "20일/60일 이동평균 골든/데드크로스"),
    StrategySpec("Momentum", {"lookback": 60, "hold": 20},
                 "60일 모멘텀 상위 → 20일 보유"),
    StrategySpec("Mean_reversion", {"z_threshold": 2.0},
                 "Z-score 2.0 이탈 시 반대 방향 진입"),
)


def run_phase65(
    stock_code: str,
    *,
    start: str,
    end: str,
    strategies: Sequence[StrategySpec] = DEFAULT_STRATEGIES,
    client: NexusMCPClient | None = None,
    fee_bps: float = 15.0,
    tax_bps: float = 20.0,
) -> list[BacktestResult]:
    """종목의 전략 시퀀스를 백테스트.

    Args:
        stock_code: 6자리 종목코드
        start: "YYYY-MM-DD"
        end: "YYYY-MM-DD"
        strategies: 실행할 전략 시퀀스. 기본 = DEFAULT_STRATEGIES
        client: `NexusMCPClient` 인스턴스 (None이면 새로 생성)
        fee_bps: 수수료 (basis points, 15 = 0.015%)
        tax_bps: 거래세 (basis points, 20 = 0.2%)

    Returns:
        `BacktestResult` 리스트.

    Raises:
        RuntimeError: MCP 호출 실패 시 (호출자가 핸들링)
    """
    mcp = client or NexusMCPClient()
    results: list[BacktestResult] = []

    for strat in strategies:
        args = {
            "stock_code": stock_code,
            "strategy": strat.name,
            "start_date": start,
            "end_date": end,
            "fee_bps": fee_bps,
            "tax_bps": tax_bps,
            **strat.params,
        }
        try:
            resp = mcp.call("backtest_run", args)
        except Exception as e:
            raise RuntimeError(f"backtest_run({strat.name}) 실패: {e}") from e
        results.append(_parse_result(strat.name, resp))

    return results


def _parse_result(strategy: str, resp: dict) -> BacktestResult:
    """MCP 응답 dict → `BacktestResult` 정규화.

    MCP 응답 형식이 버전별로 다를 수 있으므로 관대한 키 추출.
    """
    data = resp.get("result", resp)

    def _g(*keys: str, default: float = 0.0) -> float:
        for k in keys:
            if k in data:
                try:
                    return float(data[k])
                except (TypeError, ValueError):
                    continue
        return default

    return BacktestResult(
        strategy=strategy,
        total_return=_g("total_return", "return_pct", "cum_return"),
        max_drawdown=_g("max_drawdown", "mdd", "drawdown"),
        sharpe_ratio=_g("sharpe_ratio", "sharpe"),
        win_rate=_g("win_rate", "winrate"),
        raw=resp,
    )


def save_raw(results: Sequence[BacktestResult], path: str) -> None:
    """원본 MCP 응답을 `data_backtest_results.json` 으로 저장 (F4 규칙)."""
    payload = {r.strategy: r.raw for r in results}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
