"""CUFA Preflight — MCP 도구 인자 레지스트리.

Nexus MCP 도구를 호출하기 전 인자 사전 검증용 스키마.
호출 오류(인자명 오타, 필수 인자 누락)를 빌드 시점에 차단한다.

SKILL.md §10.1 TOOL_SCHEMAS 구현체.
"""
from __future__ import annotations

from typing import Any

#: 도구 스키마 레지스트리. 값은 dict로, `required` 와 `hints` 는 최소 키.
TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "dart_financial_statements": {
        "required": ("stock_code", "year", "report_type"),
        "hints": {
            "stock_code": "6자리 문자열 (ticker 아님)",
            "year": "문자열 '2024'",
            "report_type": "'CFS' or 'OFS' (대문자)",
        },
        "quirks": (
            "IS/BS/CF에 연결+별도 혼재 가능 → ord 필드로 구분",
            "당기순이익(손실) 행 중복 가능 (EPS 계산용 + 총계)",
        ),
    },
    "stocks_history": {
        "required": ("stock_code", "start_date", "end_date"),
        "hints": {
            "stock_code": "6자리 (ticker 아님)",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
        },
        "quirks": (),
    },
    "stocks_quote": {
        "required": ("stock_code",),
        "hints": {"stock_code": "6자리"},
        "quirks": ("장중이면 실시간, 장 마감이면 전일 종가",),
    },
    "backtest_run": {
        "required": ("ohlcv_data", "strategy_name"),
        "hints": {
            "ohlcv_data": "list[dict(date, open, high, low, close, volume)]",
            "strategy_name": (
                "내장 6종: RSI_oversold / MACD_crossover / Bollinger_bounce / "
                "MA_cross / Mean_reversion / Momentum"
            ),
        },
        "quirks": (),
    },
    "ecos_get_base_rate": {
        "required": (),
        "hints": {},
        "quirks": ("한국은행 기준금리, 월별 데이터",),
    },
    "ecos_get_exchange_rate": {
        "required": (),
        "hints": {"currency": "기본 'USD'"},
        "quirks": (),
    },
}


class ToolSchemaError(ValueError):
    """MCP 도구 인자 스키마 위반."""


def validate_args(tool_name: str, arguments: dict[str, Any]) -> None:
    """호출 전 인자 사전 검증.

    Args:
        tool_name: MCP 도구 이름.
        arguments: 호출 인자 dict.

    Raises:
        ToolSchemaError: 도구 미등록 또는 필수 인자 누락.
    """
    if tool_name not in TOOL_SCHEMAS:
        # 등록되지 않은 도구는 통과시키되, 개발 시 경고만.
        return

    schema = TOOL_SCHEMAS[tool_name]
    required = schema["required"]
    missing = [k for k in required if k not in arguments]
    if missing:
        hints = schema.get("hints", {})
        hint_text = "\n  ".join(f"{k}: {v}" for k, v in hints.items())
        raise ToolSchemaError(
            f"{tool_name} 인자 누락: {missing}\n힌트:\n  {hint_text}"
        )
