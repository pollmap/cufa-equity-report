"""CUFA Evaluator v2 — 표준 검증 기준 레지스트리.

HARD_MIN(필수 통과) + SMIC_STYLE(문체) + HALLUCINATION(할루시 탐지)의
모든 임계값을 한 곳에 모은 상수 클래스. SKILL.md §1.2 구현체.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvaluatorCriteria:
    """Evaluator v2 검증 기준.

    14개 HARD_MIN + 5개 SMIC_STYLE + HALLUCINATION 패턴.
    """

    # === HARD_MIN (필수 통과) ===
    TEXT_MIN: int = 80_000
    SVG_MIN: int = 25
    TABLE_MIN: int = 25
    H2H3_MIN: int = 20
    COUNTER_ARG_MIN: int = 3
    APPENDIX_MIN: int = 16
    REQUIRE_COMPLIANCE: bool = True
    REQUIRE_AI_WATERMARK: bool = True
    REQUIRE_FOOTBALL_FIELD: bool = True
    REQUIRE_SENSITIVITY: bool = True

    # === SMIC_STYLE (문체) ===
    BOLD_FIRST_MIN: int = 150
    TRANSITIONS_MIN: int = 30
    DONGSA_MIN: int = 40
    DONGSA_MAX: int = 250
    BONSEO_MIN: int = 5
    JEONSUL_MIN: int = 5
    AVG_PARA_MIN: int = 150
    AVG_PARA_MAX: int = 450

    # === HALLUCINATION 탐지 ===
    HALLUCINATION_PATTERNS: tuple[str, ...] = field(
        default_factory=lambda: (
            r"약 \d+%",
            r"대략 \d+",
            r"정도로? 추정",
            r"일반적으로 \d+",
            r"보통 \d+",
            r"통상적으로",
            r"업계 평균 \d+",
            r"할 것으로 기대된다",
            r"인 것으로 사료된다",
            r"않을까 싶다",
        )
    )

    # === 전환어 레지스트리 (TRANSITIONS_MIN 카운트 대상) ===
    TRANSITION_WORDS: tuple[str, ...] = field(
        default_factory=lambda: (
            "전술한", "전술했", "앞서 살펴본",
            "그렇다면", "그런데",
            "이에 더해", "나아가", "이와 함께",
            "한편",
            "이처럼", "이와 같이",
            "실제로",
            "다만", "그러나",
            "구체적으로",
        )
    )


#: 기본 Evaluator 기준 인스턴스.
EVAL: EvaluatorCriteria = EvaluatorCriteria()
