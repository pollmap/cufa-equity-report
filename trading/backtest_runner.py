"""
CUFA KIS Backtest — 백테스트 실행기
KIS MCP (127.0.0.1:3846)에 HTTP 요청으로 백테스트 실행

Usage:
    python trading/backtest_runner.py output/이노스페이스_strategy.yaml

Prerequisites:
    - KIS MCP 서버가 127.0.0.1:3846에서 실행중이어야 함
    - pip install requests (또는 urllib만으로도 동작)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

KIS_MCP_URL = os.environ.get("KIS_MCP_URL", "http://127.0.0.1:3846")
TIMEOUT_SEC = 60


def check_mcp_health() -> bool:
    """KIS MCP 서버 상태 확인."""
    try:
        req = Request(f"{KIS_MCP_URL}/health", method="GET")
        resp = urlopen(req, timeout=5)
        return resp.status == 200
    except (URLError, OSError):
        return False


def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """KIS MCP 도구 호출 (JSON-RPC 2.0)."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        KIS_MCP_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urlopen(req, timeout=TIMEOUT_SEC)
        result = json.loads(resp.read().decode("utf-8"))
        if "error" in result:
            return {"error": result["error"]}
        return result.get("result", {})
    except (URLError, OSError) as e:
        return {"error": f"MCP 연결 실패: {e}"}


def parse_yaml_simple(yaml_path: str) -> dict:
    """간단한 YAML 파서 (pyyaml 없이). 1-depth key: value만 지원."""
    path = Path(yaml_path)
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)

    result: dict = {}
    text = path.read_text(encoding="utf-8")

    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip()
            if val:
                # 숫자 변환 시도
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                result[key.strip()] = val

    return result


def run_backtest(strategy: dict) -> dict:
    """백테스트 실행. KIS MCP가 없으면 에러 반환."""
    # 1. MCP 연결 확인
    if not check_mcp_health():
        return {
            "error": "KIS MCP 서버 미실행 (127.0.0.1:3846)",
            "hint": "KIS MCP 서버를 먼저 실행하세요.",
        }

    # 2. 백테스트 파라미터 구성
    ticker = strategy.get("ticker", "")
    backtest_params = {
        "ticker": ticker,
        "period": "1y",
        "stop_loss_pct": strategy.get("stop_loss_pct", -15),
        "take_profit_pct": strategy.get("take_profit_pct", 30),
        "holding_period_days": strategy.get("holding_period_days", 180),
    }

    # 3. MCP 호출
    result = call_mcp_tool("backtest_run", backtest_params)

    if "error" in result:
        return result

    # 4. 결과 파싱
    return {
        "ticker": ticker,
        "win_rate": result.get("win_rate"),
        "return_pct": result.get("return_pct"),
        "max_drawdown": result.get("max_drawdown"),
        "sharpe_ratio": result.get("sharpe_ratio"),
        "trades": result.get("trades", 0),
        "raw": result,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python trading/backtest_runner.py <strategy.yaml>")
        sys.exit(1)

    strategy = parse_yaml_simple(sys.argv[1])
    print(f"Running backtest for: {strategy.get('ticker', 'unknown')}")

    result = run_backtest(strategy)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        if "hint" in result:
            print(f"HINT: {result['hint']}")
        sys.exit(1)

    print(f"\n=== Backtest Results ===")
    print(f"Win Rate: {result.get('win_rate', 'N/A')}%")
    print(f"Return: {result.get('return_pct', 'N/A')}%")
    print(f"Max Drawdown: {result.get('max_drawdown', 'N/A')}%")
    print(f"Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
    print(f"Trades: {result.get('trades', 0)}")

    # JSON 저장
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    ticker = strategy.get("ticker", "unknown")
    output_path = output_dir / f"{ticker}_backtest.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Results saved: {output_path}")


if __name__ == "__main__":
    main()
