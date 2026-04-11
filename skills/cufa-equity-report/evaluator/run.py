"""CUFA Evaluator v2 — 통합 검증 실행.

SKILL.md §8 구현체. HARD_MIN + SMIC_STYLE + HALLUCINATION을 한 번에 체크.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .criteria import EVAL, EvaluatorCriteria


@dataclass(frozen=True)
class CheckResult:
    """단일 체크 결과."""

    key: str
    passed: bool
    message: str


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluator v2 통합 결과."""

    passed_count: int
    total_count: int
    checks: tuple[CheckResult, ...]
    hallucinations: tuple[str, ...] = field(default_factory=tuple)

    @property
    def all_passed(self) -> bool:
        return self.passed_count == self.total_count

    def format_report(self) -> str:
        header = f"=== Evaluator v2 — {self.passed_count} / {self.total_count} PASS ==="
        lines = [header]
        for c in self.checks:
            mark = "[PASS]" if c.passed else "[FAIL]"
            lines.append(f"  {mark} {c.key:20s} {c.message}")
        if self.hallucinations:
            lines.append("")
            lines.append("=== HALLUCINATION WARNINGS ===")
            for h in self.hallucinations:
                lines.append(f"  ⚠ {h}")
        return "\n".join(lines)

    def failing_keys(self) -> tuple[str, ...]:
        return tuple(c.key for c in self.checks if not c.passed)


def _text_only(html: str) -> str:
    """HTML → 순수 텍스트 (공백 정규화)."""
    text = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", text).strip()


def _count_bold_first(html: str) -> int:
    """`<p><strong>…</strong>` 패턴의 첫문장 볼드 개수."""
    return len(re.findall(r"<p[^>]*>\s*<strong[^>]*>", html))


def _count_transitions(html: str, words: tuple[str, ...]) -> int:
    total = 0
    for w in words:
        total += html.count(w)
    return total


def _avg_paragraph_length(html: str) -> float:
    """`<p>` 태그 평균 자수 (공백 포함)."""
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
    if not paragraphs:
        return 0.0
    texts = [re.sub(r"<[^>]+>", "", p).strip() for p in paragraphs]
    texts = [t for t in texts if t]
    if not texts:
        return 0.0
    return sum(len(t) for t in texts) / len(texts)


def _check_hard_min(
    html: str,
    text_chars: int,
    criteria: EvaluatorCriteria,
) -> list[CheckResult]:
    """14개 HARD_MIN 체크."""
    svg_count = html.count("<svg ")
    table_count = html.count("<table")
    h2_count = html.count("<h2")
    h3_count = html.count("<h3")
    h2h3 = h2_count + h3_count
    counter_count = html.count("시장의 우려") + html.count('class="counter-arg"')
    appendix_count = html.count("Appendix A-") + html.count("A-1.")

    results = [
        CheckResult("text_min",    text_chars >= criteria.TEXT_MIN,
                    f"text {text_chars:,} / {criteria.TEXT_MIN:,}"),
        CheckResult("svg_min",     svg_count >= criteria.SVG_MIN,
                    f"svg {svg_count} / {criteria.SVG_MIN}"),
        CheckResult("table_min",   table_count >= criteria.TABLE_MIN,
                    f"tables {table_count} / {criteria.TABLE_MIN}"),
        CheckResult("h2h3_min",    h2h3 >= criteria.H2H3_MIN,
                    f"h2+h3 {h2h3} / {criteria.H2H3_MIN}"),
        CheckResult("counter_arg", counter_count >= criteria.COUNTER_ARG_MIN,
                    f"counter_arg {counter_count} / {criteria.COUNTER_ARG_MIN}"),
        CheckResult("appendix",    appendix_count >= criteria.APPENDIX_MIN,
                    f"appendix {appendix_count} / {criteria.APPENDIX_MIN}"),
    ]

    if criteria.REQUIRE_COMPLIANCE:
        ok = "Compliance Notice" in html
        results.append(CheckResult("compliance", ok, f"Compliance Notice: {ok}"))
    if criteria.REQUIRE_AI_WATERMARK:
        ok = "AI-Assisted" in html
        results.append(CheckResult("ai_watermark", ok, f"AI-Assisted: {ok}"))
    if criteria.REQUIRE_FOOTBALL_FIELD:
        ok = "Football" in html or "football" in html
        results.append(CheckResult("football", ok, f"Football Field: {ok}"))
    if criteria.REQUIRE_SENSITIVITY:
        ok = "민감도" in html
        results.append(CheckResult("sensitivity", ok, f"민감도: {ok}"))

    return results


def _check_smic_style(
    html: str,
    criteria: EvaluatorCriteria,
) -> list[CheckResult]:
    """SMIC 문체 체크."""
    bold_first = _count_bold_first(html)
    transitions = _count_transitions(html, criteria.TRANSITION_WORDS)
    dongsa = html.count("동사")
    bonseo = html.count("본서는") + html.count("본서에")
    jeonsul = html.count("전술한") + html.count("전술했")
    avg_para = _avg_paragraph_length(html)

    return [
        CheckResult("bold_first_min", bold_first >= criteria.BOLD_FIRST_MIN,
                    f"bold-first {bold_first} / {criteria.BOLD_FIRST_MIN}"),
        CheckResult("transitions_min", transitions >= criteria.TRANSITIONS_MIN,
                    f"transitions {transitions} / {criteria.TRANSITIONS_MIN}"),
        CheckResult("dongsa_range",
                    criteria.DONGSA_MIN <= dongsa <= criteria.DONGSA_MAX,
                    f'"동사" {dongsa} (range {criteria.DONGSA_MIN}~{criteria.DONGSA_MAX})'),
        CheckResult("bonseo_min", bonseo >= criteria.BONSEO_MIN,
                    f'"본서" {bonseo} / {criteria.BONSEO_MIN}'),
        CheckResult("jeonsul_min", jeonsul >= criteria.JEONSUL_MIN,
                    f'"전술" {jeonsul} / {criteria.JEONSUL_MIN}'),
        CheckResult("avg_para_range",
                    criteria.AVG_PARA_MIN <= avg_para <= criteria.AVG_PARA_MAX,
                    f"avg_para {avg_para:.0f} (range {criteria.AVG_PARA_MIN}~{criteria.AVG_PARA_MAX})"),
    ]


def _detect_hallucinations(
    html: str,
    criteria: EvaluatorCriteria,
) -> tuple[str, ...]:
    """할루시네이션 패턴 탐지."""
    matches: list[str] = []
    for pattern in criteria.HALLUCINATION_PATTERNS:
        found = re.findall(pattern, html)
        if found:
            matches.append(f'{pattern}: {found[:3]}')
    return tuple(matches)


def evaluate(
    html: str,
    criteria: EvaluatorCriteria = EVAL,
) -> EvaluationResult:
    """HTML 보고서에 대한 통합 검증 실행.

    Args:
        html: 빌드된 HTML 문자열.
        criteria: 검증 기준 (기본 `EVAL`).

    Returns:
        EvaluationResult — 모든 체크 결과 + 할루시네이션.
    """
    text_chars = len(_text_only(html))
    hard = _check_hard_min(html, text_chars, criteria)
    smic = _check_smic_style(html, criteria)
    hallu = _detect_hallucinations(html, criteria)

    all_checks = tuple(hard + smic)
    passed = sum(1 for c in all_checks if c.passed)
    return EvaluationResult(
        passed_count=passed,
        total_count=len(all_checks),
        checks=all_checks,
        hallucinations=hallu,
    )
