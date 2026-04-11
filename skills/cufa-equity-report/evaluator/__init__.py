"""CUFA Evaluator v2 — 품질 자동 검증 모듈.

공개 API:
    EVAL                : 기본 검증 기준 (EvaluatorCriteria)
    EvaluatorCriteria   : 상수 클래스
    evaluate            : 통합 검증 실행
    EvaluationResult    : 결과 구조체
"""
from __future__ import annotations

from .criteria import EVAL, EvaluatorCriteria
from .run import EvaluationResult, evaluate

__all__ = [
    "EVAL",
    "EvaluatorCriteria",
    "EvaluationResult",
    "evaluate",
]
