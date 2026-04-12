"""CUFA Evaluator v3 — 통합 실행가능성 검증.

v2(분량 카운팅) → v3(actionability regex 탐지) 전환.
12개 binary 체크 + 할루시네이션 경고.

SKILL.md §8 구현체.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .criteria import EVAL_V3, EvaluatorV3Criteria


# ---------------------------------------------------------------------------
# Result Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CheckResult:
    """단일 체크 결과."""
    key: str
    passed: bool
    message: str


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluator v3 통합 결과."""
    passed_count: int
    total_count: int
    checks: tuple[CheckResult, ...]
    hallucinations: tuple[str, ...] = field(default_factory=tuple)

    @property
    def all_passed(self) -> bool:
        return self.passed_count == self.total_count

    def format_report(self) -> str:
        header = f"=== Evaluator v3 — {self.passed_count} / {self.total_count} PASS ==="
        if self.all_passed:
            header += " ✅ ALL PASS"
        lines = [header, ""]
        for c in self.checks:
            mark = "[PASS]" if c.passed else "[FAIL]"
            lines.append(f"  {mark} {c.key:<30s}  {c.message}")
        if self.hallucinations:
            lines.append("")
            lines.append("=== HALLUCINATION WARNINGS (참조, 실패 아님) ===")
            for h in self.hallucinations:
                lines.append(f"  ⚠  {h}")
        return "\n".join(lines)

    def failing_keys(self) -> tuple[str, ...]:
        return tuple(c.key for c in self.checks if not c.passed)


# ---------------------------------------------------------------------------
# Detection Helpers
# ---------------------------------------------------------------------------

def _text_only(html: str) -> str:
    """HTML → 순수 텍스트."""
    text = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", text).strip()


def _has_opinion(html: str) -> bool:
    """BUY / HOLD / SELL / WATCH / AVOID 중 하나 포함."""
    return bool(re.search(
        r'\b(BUY|HOLD|SELL|WATCH|AVOID|매수|매도|중립|보유)\b',
        html, re.IGNORECASE
    ))


def _has_target_price(html: str) -> bool:
    """목표주가 숫자 — 'TP' 또는 '목표주가' + 숫자(원)."""
    return bool(re.search(
        r'(TP|목표주가|target_price)\D{0,20}[\d,]{3,}',
        html, re.IGNORECASE
    ))


def _has_stop_loss(html: str) -> bool:
    """손절가 또는 stop_loss 숫자."""
    return bool(re.search(
        r'(손절가?|stop_loss|SL)\D{0,20}[\d,]{3,}',
        html, re.IGNORECASE
    ))


def _has_position_size(html: str) -> bool:
    """position_size_pct 또는 포지션 비중 %."""
    return bool(re.search(
        r'(position_size_pct|포지션.{0,5}비중|비중.{0,5}%)\D{0,10}[\d.]+',
        html, re.IGNORECASE
    ))


def _has_bear_floor(html: str) -> bool:
    """Bear Case 가격 또는 하방 언급."""
    return bool(re.search(
        r'(Bear|하방|최악|bear_price|최저.{0,5}[원주가])',
        html, re.IGNORECASE
    ))


def _count_kill_conditions(html: str) -> int:
    """kill_condition 또는 '매도 조건', 'Kill Condition' 개수."""
    count = len(re.findall(r'kill.condition', html, re.IGNORECASE))
    count += len(re.findall(r'(매도 조건|투자 논리 훼손|Kill)', html))
    count += html.count("kill_")
    # Also count list items inside kill conditions sections
    in_kill = re.search(
        r'(kill.condition|Kill Condition|매도 조건)(.*?)(</section>|<h[2-3])',
        html, re.IGNORECASE | re.DOTALL
    )
    if in_kill:
        items = len(re.findall(r'<li', in_kill.group(2)))
        count = max(count, items)
    return count


def _count_catalysts(html: str) -> int:
    """날짜 붙은 Catalyst 이벤트 개수."""
    # Look for patterns like "2025Q3", "2026-01", "25년", "Q1 2026"
    date_patterns = [
        r'\d{4}[년Q/\-]\s*[0-9Q]',   # 2025Q3, 2026-01, 2025년 Q1
        r'Q[1-4]\s*\d{4}',           # Q3 2025
        r'\d{2}년 \d{1,2}월',        # 26년 3월
    ]
    total = 0
    for pat in date_patterns:
        total += len(re.findall(pat, html))
    return total


def _has_trade_ticket(html: str) -> bool:
    """Trade Ticket 블록 또는 YAML 존재."""
    return bool(re.search(
        r'(trade.ticket|trade_ticket|ticket-box|ticket_yaml|\.ticket-yaml)',
        html, re.IGNORECASE
    ))


def _has_data_sources(html: str) -> bool:
    """데이터 출처 1건 이상."""
    return bool(re.search(
        r'(DART|KRX|ECOS|Nexus MCP|Bloomberg|FnGuide|출처|Source)',
        html, re.IGNORECASE
    ))


def _has_backtest_hook(html: str) -> bool:
    """Backtest engine 연동 여부."""
    return bool(re.search(
        r'(backtest|QuantPipeline|open.trading.api|백테스트)',
        html, re.IGNORECASE
    ))


def _has_falsifiable_thesis(html: str) -> bool:
    """반증 조건 — 'Kill' / 'Condition' / '틀리면' / '이 가정이' 등."""
    return bool(re.search(
        r'(틀리면|무효화|훼손|반증|falsif|Kill Condition|논리가.{0,10}깨지)',
        html, re.IGNORECASE
    ))


def _has_risk_reward(html: str) -> bool:
    """Risk/Reward 수치."""
    return bool(re.search(
        r'(Risk.?Reward|R/R|risk_reward)\D{0,20}\d+\.?\d*[x배]?',
        html, re.IGNORECASE
    ))


def _detect_hallucinations(
    html: str,
    criteria: EvaluatorV3Criteria,
) -> tuple[str, ...]:
    matches: list[str] = []
    for pattern in criteria.HALLUCINATION_PATTERNS:
        found = re.findall(pattern, html)
        if found:
            matches.append(f'{pattern}: {found[:3]}')
    return tuple(matches)


# ---------------------------------------------------------------------------
# Main Evaluate Function
# ---------------------------------------------------------------------------

def evaluate(
    html: str,
    criteria: EvaluatorV3Criteria = EVAL_V3,
) -> EvaluationResult:
    """HTML 보고서에 대한 Evaluator v3 실행가능성 검증.

    Args:
        html:     빌드된 HTML 문자열.
        criteria: 검증 기준 (기본 EVAL_V3).

    Returns:
        EvaluationResult — 12개 binary 체크 결과.
    """
    checks: list[CheckResult] = []

    # 1. Opinion
    if criteria.REQUIRE_OPINION:
        ok = _has_opinion(html)
        checks.append(CheckResult("opinion", ok,
            "BUY/HOLD/SELL 명시" if ok else "투자의견 미발견"))

    # 2. Target Price
    if criteria.REQUIRE_TARGET_PRICE:
        ok = _has_target_price(html)
        checks.append(CheckResult("target_price", ok,
            "목표주가 확인" if ok else "목표주가 숫자 미발견"))

    # 3. Stop Loss
    if criteria.REQUIRE_STOP_LOSS:
        ok = _has_stop_loss(html)
        checks.append(CheckResult("stop_loss", ok,
            "손절가 확인" if ok else "손절가 미설정 — 리스크 관리 불가"))

    # 4. Position Size
    if criteria.REQUIRE_POSITION_SIZE:
        ok = _has_position_size(html)
        checks.append(CheckResult("position_size", ok,
            "포지션 비중 확인" if ok else "position_size_pct 미기재"))

    # 5. Bear Floor
    if criteria.REQUIRE_BEAR_FLOOR:
        ok = _has_bear_floor(html)
        checks.append(CheckResult("bear_floor", ok,
            "Bear Case 하방 확인" if ok else "Bear Case 미기재"))

    # 6. Kill Conditions
    kc_count = _count_kill_conditions(html)
    ok = kc_count >= criteria.REQUIRE_KILL_CONDITIONS_MIN
    checks.append(CheckResult("kill_conditions", ok,
        f"Kill Condition {kc_count}건 ≥ {criteria.REQUIRE_KILL_CONDITIONS_MIN}" if ok
        else f"Kill Condition {kc_count}건 < {criteria.REQUIRE_KILL_CONDITIONS_MIN}건 필요"))

    # 7. Catalyst Timeline
    cat_count = _count_catalysts(html)
    ok = cat_count >= criteria.REQUIRE_CATALYST_TIMELINE_MIN
    checks.append(CheckResult("catalyst_timeline", ok,
        f"Catalyst {cat_count}건 ≥ {criteria.REQUIRE_CATALYST_TIMELINE_MIN}" if ok
        else f"Catalyst {cat_count}건 < {criteria.REQUIRE_CATALYST_TIMELINE_MIN}건 필요"))

    # 8. Trade Ticket
    if criteria.REQUIRE_TRADE_TICKET:
        ok = _has_trade_ticket(html)
        checks.append(CheckResult("trade_ticket", ok,
            "Trade Ticket 확인" if ok else "Trade Ticket YAML 미발견"))

    # 9. Data Sources
    if criteria.REQUIRE_DATA_SOURCES:
        ok = _has_data_sources(html)
        checks.append(CheckResult("data_sources", ok,
            "데이터 출처 확인" if ok else "데이터 출처 미기재"))

    # 10. Backtest Hook
    if criteria.REQUIRE_BACKTEST_HOOK:
        ok = _has_backtest_hook(html)
        checks.append(CheckResult("backtest_hook", ok,
            "Backtest 연동 확인" if ok else "QuantPipeline 연동 미기재"))

    # 11. Falsifiable Thesis
    if criteria.REQUIRE_FALSIFIABLE_THESIS:
        ok = _has_falsifiable_thesis(html)
        checks.append(CheckResult("falsifiable_thesis", ok,
            "반증 조건 확인" if ok else "반증 조건 미기재 — 'Kill Condition' 추가 필요"))

    # 12. Risk/Reward
    if criteria.REQUIRE_RISK_REWARD:
        ok = _has_risk_reward(html)
        checks.append(CheckResult("risk_reward", ok,
            "R/R 수치 확인" if ok else "Risk/Reward 비율 미기재"))

    # Hallucination (참조)
    hallu = _detect_hallucinations(html, criteria)
    passed = sum(1 for c in checks if c.passed)

    return EvaluationResult(
        passed_count=passed,
        total_count=len(checks),
        checks=tuple(checks),
        hallucinations=hallu,
    )
