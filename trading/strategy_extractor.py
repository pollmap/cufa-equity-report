"""
CUFA KIS Backtest — 매매전략 추출기
config.py의 INVESTMENT_POINTS → 매매전략 YAML 변환

Usage:
    python trading/strategy_extractor.py examples/이노스페이스/config.py
    → output/이노스페이스_strategy.yaml
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_config(config_path: str) -> ModuleType:
    """config.py를 모듈로 로드."""
    path = Path(config_path).resolve()
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_strategy(cfg: ModuleType) -> dict:
    """config에서 매매전략 dict 추출."""
    ticker = cfg.TICKER
    name = cfg.COMPANY_NAME
    price = getattr(cfg, "CURRENT_PRICE", 0)
    ips = getattr(cfg, "INVESTMENT_POINTS", [])
    risks = getattr(cfg, "RISKS", [])
    kill_conds = getattr(cfg, "KILL_CONDITIONS", [])

    # IP에서 진입/이탈 조건 추출
    entry_conditions: list[str] = []
    exit_conditions: list[str] = []

    for ip in ips:
        chain = ip.get("chain", [])
        if chain:
            # 마지막 단계 = 결론 → 진입 조건
            entry_conditions.append(chain[-1])
        if ip.get("subtitle"):
            entry_conditions.append(ip["subtitle"])

    # 리스크에서 이탈 조건 추출
    for r in risks:
        if r.get("probability", 0) >= 50:
            exit_conditions.append(f'{r["name"]} 현실화 (확률 {r.get("probability")}%)')

    # Kill Conditions → 강제 이탈
    for kc in kill_conds:
        exit_conditions.append(f'Kill: {kc["condition"]}')

    strategy = {
        "ticker": ticker,
        "name": name,
        "current_price": price,
        "entry": {
            "conditions": entry_conditions,
            "price_range": {
                "min": int(price * 0.9),
                "max": int(price * 1.05),
            },
        },
        "exit": {
            "conditions": exit_conditions,
            "stop_loss_pct": -15,
            "take_profit_pct": 30,
        },
        "holding_period_days": 180,
        "position_size_pct": 5,
    }

    return strategy


def to_yaml(strategy: dict, indent: int = 0) -> str:
    """dict → YAML 문자열 (pyyaml 없이 수동 변환)."""
    lines: list[str] = []
    prefix = "  " * indent

    for key, val in strategy.items():
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(to_yaml(val, indent + 1))
        elif isinstance(val, list):
            lines.append(f"{prefix}{key}:")
            for item in val:
                lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}{key}: {val}")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python trading/strategy_extractor.py <config.py>")
        sys.exit(1)

    cfg = load_config(sys.argv[1])
    strategy = extract_strategy(cfg)
    yaml_str = to_yaml(strategy)

    # 출력
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{cfg.COMPANY_NAME}_strategy.yaml"
    output_path.write_text(yaml_str, encoding="utf-8")

    print(f"Strategy extracted: {output_path}")
    print(yaml_str)


if __name__ == "__main__":
    main()
