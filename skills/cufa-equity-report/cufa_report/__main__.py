"""
python -m cufa_report — CUFA Equity Report v16 CLI 진입점.

Usage:
    python -m cufa_report <stock_code> [options]

Examples:
    python -m cufa_report 329180 --opinion BUY --tp 528750 --sl 410000
    python -m cufa_report 329180 --evaluate output/report.html
    python -m cufa_report 329180 --ticket-only --entry 475000

Options:
    --opinion   BUY|HOLD|SELL|WATCH|AVOID (default: HOLD)
    --tp        목표주가 (원)
    --sl        손절가 (원)
    --entry     진입기준가 (원, default: tp 또는 0)
    --size      포지션 비중 % (default: 3.0)
    --evaluate  HTML 파일 경로 → Evaluator v3 실행
    --ticket-only  Trade Ticket YAML만 출력 (빌드 없음)
    --output    출력 디렉터리 (default: ./output)
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Windows 터미널 인코딩 강제 UTF-8 (cp949 깨짐 방지)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 스킬 루트(cufa_report의 부모)를 sys.path에 추가
_SKILL_ROOT = Path(__file__).parent.parent
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m cufa_report",
        description="CUFA Equity Report v16 — 1인 AI 퀀트 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # Evaluator v3 실행
  python -m cufa_report 329180 --evaluate output/HD현대중공업_CUFA.html

  # Trade Ticket YAML 생성 (빠른 확인)
  python -m cufa_report 329180 --ticket-only --tp 528750 --sl 410000 --entry 475000

  # 완전 CLI 파라미터
  python -m cufa_report 329180 --opinion BUY --tp 528750 --sl 410000 --size 5.0
""",
    )
    p.add_argument("stock_code", help="종목코드 (6자리, 예: 329180)")
    p.add_argument("--opinion", choices=["BUY", "HOLD", "SELL", "WATCH", "AVOID"],
                   default="HOLD", help="투자의견 (default: HOLD)")
    p.add_argument("--tp", type=int, default=0, metavar="PRICE", help="목표주가 (원)")
    p.add_argument("--sl", type=int, default=0, metavar="PRICE", help="손절가 (원)")
    p.add_argument("--entry", type=int, default=0, metavar="PRICE", help="진입기준가 (원)")
    p.add_argument("--size", type=float, default=3.0, metavar="PCT",
                   help="포지션 비중 %% (0~20, default: 3.0)")
    p.add_argument("--evaluate", metavar="HTML_PATH",
                   help="기존 HTML 보고서에 Evaluator v3 실행 후 리포트 출력")
    p.add_argument("--ticket-only", action="store_true",
                   help="Trade Ticket YAML만 stdout에 출력 (빌드 없음)")
    p.add_argument("--output", default="output", metavar="DIR",
                   help="출력 디렉터리 (default: ./output)")
    return p


def cmd_evaluate(html_path: str) -> int:
    """기존 HTML 보고서에 Evaluator v3 실행."""
    from evaluator.run import evaluate

    path = Path(html_path)
    if not path.exists():
        print(f"[ERROR] 파일 없음: {html_path}", file=sys.stderr)
        return 1

    html = path.read_text(encoding="utf-8")
    result = evaluate(html)
    print(result.format_report())
    return 0 if result.all_passed else 1


def cmd_ticket_only(args: argparse.Namespace) -> int:
    """Trade Ticket YAML을 stdout으로 출력."""
    from trade_ticket.schema import (
        TradeOpinion,
        TradeTicket,
        ticket_to_yaml,
        validate_trade_ticket,
    )
    from trade_ticket.generator import _compute_risk_reward

    ticker = f"{args.stock_code}.KS"
    entry = args.entry or args.tp or 0
    rr = _compute_risk_reward(entry, args.sl, args.tp)

    try:
        opinion = TradeOpinion(args.opinion)
    except ValueError:
        opinion = TradeOpinion.HOLD

    ticket = TradeTicket(
        ticker=ticker,
        company_name=f"종목 {args.stock_code}",
        opinion=opinion,
        entry_price=entry,
        stop_loss=args.sl,
        target_price=args.tp,
        position_size_pct=args.size,
        risk_reward=rr,
        backtest_engine="open-trading-api/QuantPipeline",
        data_sources=["DART", "KRX"],
    )

    errors = validate_trade_ticket(ticket)
    if errors:
        print("=== Trade Ticket 검증 오류 ===", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)

    yaml = ticket_to_yaml(ticket)
    print(yaml)
    return 1 if errors else 0


def cmd_info(args: argparse.Namespace) -> int:
    """기본 모드: 종목 정보 요약 출력."""
    ticker = f"{args.stock_code}.KS"
    entry = args.entry or args.tp or 0

    print(f"=== CUFA Equity Report v16 ===")
    print(f"종목: {ticker}")
    print(f"의견: {args.opinion}")
    if args.tp:
        print(f"목표주가: {args.tp:,}원")
    if args.sl:
        print(f"손절가:   {args.sl:,}원")
    if entry and args.sl:
        from trade_ticket.generator import _compute_risk_reward
        rr = _compute_risk_reward(entry, args.sl, args.tp)
        print(f"R/R:      {rr:.2f}x")
    print(f"포지션:   {args.size}%")
    print("")
    print("다음 단계:")
    print("  1. config/{stock_code}.py 작성 후 Phase 0~6 실행")
    print("  2. --ticket-only 로 Trade Ticket 먼저 확인")
    print("  3. HTML 빌드 후 --evaluate 로 Evaluator v3 검증")
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.evaluate:
        sys.exit(cmd_evaluate(args.evaluate))
    elif args.ticket_only:
        sys.exit(cmd_ticket_only(args))
    else:
        sys.exit(cmd_info(args))


if __name__ == "__main__":
    main()
