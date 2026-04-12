"""
Backtest Hook — CUFA Equity Report v16

Bridges a Trade Ticket to open-trading-api / QuantPipeline.

Flow:
    TradeTicket (YAML) → submit_to_backtest() → QuantPipeline.run()
                      → BacktestResult → saved to data/backtest/

The backtest engine path is resolved relative to the environment variable
OPEN_TRADING_API_PATH, falling back to ~/Desktop/open-trading-api.

Interface contract:
    BacktestResult.deviation_pct — how far actual return deviated from TP
    BacktestResult.hit_kill     — which kill condition triggered (if any)
    BacktestResult.max_drawdown — realized max drawdown %

These feed into feedback.py (Phase 7).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .schema import TradeTicket


# ---------------------------------------------------------------------------
# Result Schema
# ---------------------------------------------------------------------------

@dataclass
class BacktestResult:
    ticker: str
    period_start: str           # ISO date
    period_end: str             # ISO date
    entry_price: int
    exit_price: int
    stop_loss: int
    target_price: int
    realized_return_pct: float  # actual PnL %
    hit_stop: bool = False
    hit_target: bool = False
    hit_kill: str | None = None             # kill condition that fired
    max_drawdown_pct: float = 0.0
    deviation_pct: float = 0.0             # (actual - estimated TP)/ estimated TP
    backtest_engine: str = "open-trading-api/QuantPipeline"
    raw: dict[str, Any] = field(default_factory=dict)   # full engine output


# ---------------------------------------------------------------------------
# Path Resolution
# ---------------------------------------------------------------------------

def _resolve_quant_pipeline_path() -> Path | None:
    """Find QuantPipeline in open-trading-api."""
    env_path = os.environ.get("OPEN_TRADING_API_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates += [
        Path.home() / "Desktop" / "open-trading-api",
        Path("/root/Desktop/open-trading-api"),
        Path("/opt/open-trading-api"),
    ]
    for p in candidates:
        pipeline = p / "backtester" / "core" / "pipeline.py"
        if pipeline.exists():
            return p / "backtester"
    return None


# ---------------------------------------------------------------------------
# Main Interface
# ---------------------------------------------------------------------------

def submit_to_backtest(
    ticket: TradeTicket,
    output_dir: Path | None = None,
) -> BacktestResult | None:
    """
    Submit a TradeTicket to the QuantPipeline backtester.

    Returns:
        BacktestResult if pipeline found and succeeds.
        None if pipeline not found (logs a warning).
    """
    pipeline_dir = _resolve_quant_pipeline_path()
    if pipeline_dir is None:
        print(
            "[backtest_hook] WARNING: open-trading-api not found. "
            "Set OPEN_TRADING_API_PATH or install to ~/Desktop/open-trading-api"
        )
        return None

    # Dynamically load QuantPipeline
    spec = importlib.util.spec_from_file_location(
        "pipeline", pipeline_dir / "core" / "pipeline.py"
    )
    if spec is None or spec.loader is None:
        print("[backtest_hook] ERROR: Failed to load pipeline.py spec")
        return None

    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(pipeline_dir.parent))
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as e:
        print(f"[backtest_hook] ERROR loading QuantPipeline: {e}")
        return None

    # Build pipeline config from TradeTicket
    pipeline_config = {
        "ticker": ticket.ticker,
        "entry_price": ticket.entry_price,
        "stop_loss": ticket.stop_loss,
        "target_price": ticket.target_price,
        "horizon_months": ticket.horizon_months,
        "position_size_pct": ticket.position_size_pct,
        **ticket.backtest_config,
    }

    try:
        pipeline = module.QuantPipeline(pipeline_config)
        raw_result = pipeline.run()
    except Exception as e:
        print(f"[backtest_hook] ERROR running QuantPipeline: {e}")
        return None

    # Parse result
    result = BacktestResult(
        ticker=ticket.ticker,
        period_start=raw_result.get("period_start", date.today().isoformat()),
        period_end=raw_result.get("period_end", date.today().isoformat()),
        entry_price=ticket.entry_price,
        exit_price=raw_result.get("exit_price", ticket.entry_price),
        stop_loss=ticket.stop_loss,
        target_price=ticket.target_price,
        realized_return_pct=raw_result.get("return_pct", 0.0),
        hit_stop=raw_result.get("hit_stop", False),
        hit_target=raw_result.get("hit_target", False),
        hit_kill=raw_result.get("hit_kill"),
        max_drawdown_pct=raw_result.get("max_drawdown_pct", 0.0),
        backtest_engine=ticket.backtest_engine,
        raw=raw_result,
    )

    # Compute deviation from TP estimate
    if ticket.target_price > 0:
        result.deviation_pct = round(
            (result.exit_price - ticket.target_price) / ticket.target_price * 100, 2
        )

    # Persist result
    if output_dir is None:
        output_dir = Path.cwd() / "data" / "backtest"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / f"{ticket.ticker}_{date.today().isoformat()}_backtest.json"
    with result_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "ticker": result.ticker,
                "period": f"{result.period_start} ~ {result.period_end}",
                "entry": result.entry_price,
                "exit": result.exit_price,
                "stop": result.stop_loss,
                "target": result.target_price,
                "realized_return_pct": result.realized_return_pct,
                "deviation_pct": result.deviation_pct,
                "hit_stop": result.hit_stop,
                "hit_target": result.hit_target,
                "hit_kill": result.hit_kill,
                "max_drawdown_pct": result.max_drawdown_pct,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"[backtest_hook] Result saved: {result_path}")
    return result
