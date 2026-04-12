"""
Trade Ticket Generator — CUFA Equity Report v16

Converts a StockConfig (config/_template.py) into a validated TradeTicket.
Called at the end of Phase 6 (HTML Build) to produce the YAML artifact.

Usage:
    from trade_ticket.generator import generate_trade_ticket
    from trade_ticket.schema import ticket_to_yaml, validate_trade_ticket

    ticket = generate_trade_ticket(config)
    errors = validate_trade_ticket(ticket)
    if not errors:
        yaml_str = ticket_to_yaml(ticket)
        with open("trade_ticket.yaml", "w", encoding="utf-8") as f:
            f.write(yaml_str)
"""

from __future__ import annotations

import math
from datetime import date
from typing import TYPE_CHECKING, Any

from .schema import (
    CatalystEvent,
    ScenarioBand,
    TradeOpinion,
    TradeTicket,
    validate_trade_ticket,
)

if TYPE_CHECKING:
    pass  # StockConfig imported at runtime to avoid circular dep


def _compute_risk_reward(entry: int, stop: int, target: int) -> float:
    """Risk/Reward = |target - entry| / |entry - stop|"""
    denom = abs(entry - stop)
    if denom == 0:
        return 0.0
    return round(abs(target - entry) / denom, 2)


def generate_trade_ticket(config: Any) -> TradeTicket:
    """
    Build a TradeTicket from a StockConfig-like object.

    Expected config attributes (all optional with sensible defaults):
        config.META          — {ticker, company_name}
        config.PRICE         — {current}
        config.TARGET_PRICE  — {weighted, upside_pct, risk_reward}
        config.TRADE_TICKET  — {stop_loss, position_size_pct, entry_price,
                                 horizon_months, opinion}
        config.KILL_CONDITIONS  — list[str]
        config.CATALYST_TIMELINE — list[{date, event, upside_delta_pct?}]
        config.VALUATION_SCENARIOS — {bear/base/bull probs/prices}
        config.BACKTEST_CONFIG   — dict
        config.DATA_SOURCES      — list[str]
    """
    meta = getattr(config, "META", {})
    price_data = getattr(config, "PRICE", {})
    target_data = getattr(config, "TARGET_PRICE", {})
    tt_data = getattr(config, "TRADE_TICKET", {})
    kill_conditions = getattr(config, "KILL_CONDITIONS", [])
    catalysts_raw = getattr(config, "CATALYST_TIMELINE", [])
    scenario_raw = getattr(config, "VALUATION_SCENARIOS", {})
    backtest_cfg = getattr(config, "BACKTEST_CONFIG", {})
    data_sources = getattr(config, "DATA_SOURCES", [])

    # Resolve values with fallback chain
    ticker = meta.get("ticker", "")
    company_name = meta.get("company_name", meta.get("name", ""))
    current_price = price_data.get("current", 0)
    target_price = target_data.get("weighted", target_data.get("base", 0))

    # Trade Ticket overrides
    opinion_str = tt_data.get("opinion", _infer_opinion(target_price, current_price))
    try:
        opinion = TradeOpinion(opinion_str.upper())
    except ValueError:
        opinion = TradeOpinion.HOLD

    entry_price = tt_data.get("entry_price", current_price)
    stop_loss = tt_data.get("stop_loss", 0)
    horizon = tt_data.get("horizon_months", 12)
    position_pct = tt_data.get("position_size_pct", 3.0)

    rr = _compute_risk_reward(entry_price, stop_loss, target_price)

    # Catalyst events
    catalyst_events = [
        CatalystEvent(
            date=c.get("date", ""),
            event=c.get("event", ""),
            upside_delta_pct=c.get("upside_delta_pct"),
        )
        for c in catalysts_raw
    ]

    # Scenario band
    scenario = None
    if scenario_raw:
        bear = scenario_raw.get("bear", {})
        base = scenario_raw.get("base", {})
        bull = scenario_raw.get("bull", {})
        if bear and base and bull:
            scenario = ScenarioBand(
                bear_price=bear.get("price", 0),
                base_price=base.get("price", target_price),
                bull_price=bull.get("price", 0),
                bear_prob=bear.get("prob", 0.25),
                base_prob=base.get("prob", 0.50),
                bull_prob=bull.get("prob", 0.25),
            )

    ticket = TradeTicket(
        ticker=ticker,
        company_name=company_name,
        report_version="v16",
        opinion=opinion,
        entry_price=entry_price,
        stop_loss=stop_loss,
        target_price=target_price,
        horizon_months=horizon,
        position_size_pct=position_pct,
        risk_reward=rr,
        kill_conditions=list(kill_conditions),
        catalyst_timeline=catalyst_events,
        scenario=scenario,
        backtest_engine=backtest_cfg.get("engine", "open-trading-api/QuantPipeline"),
        backtest_config=backtest_cfg,
        generated_at=date.today().isoformat(),
        analyst="Luxon AI / CUFA",
        data_sources=list(data_sources),
    )

    return ticket


def _infer_opinion(target_price: int, current_price: int) -> str:
    """Infer BUY/HOLD/SELL from upside if opinion not explicitly set."""
    if current_price <= 0:
        return "HOLD"
    upside = (target_price - current_price) / current_price
    if upside >= 0.15:
        return "BUY"
    if upside >= -0.05:
        return "HOLD"
    return "SELL"
