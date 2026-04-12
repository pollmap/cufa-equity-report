"""
trade_ticket — CUFA Equity Report v16 Trade Ticket Module

Converts StockConfig data into a machine-readable YAML Trade Ticket
that feeds directly into open-trading-api / QuantPipeline.

Pipeline:
    StockConfig → generator.py → TradeTicket (schema.py)
                → YAML output → backtest_hook.py → QuantPipeline
                → actual results → feedback.py → Phase 7 review
"""

from .schema import TradeTicket, TradeOpinion, validate_trade_ticket
from .generator import generate_trade_ticket
from .backtest_hook import submit_to_backtest
from .feedback import run_feedback_loop

__all__ = [
    "TradeTicket",
    "TradeOpinion",
    "validate_trade_ticket",
    "generate_trade_ticket",
    "submit_to_backtest",
    "run_feedback_loop",
]
