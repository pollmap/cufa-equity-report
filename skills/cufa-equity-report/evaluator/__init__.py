"""CUFA Evaluator v3 — 실행가능성(Actionability) 자동 검증 모듈.

공개 API:
    EVAL_V3              : 기본 검증 기준 (EvaluatorV3Criteria)
    EVAL                 : EVAL_V3 하위호환 alias
    EvaluatorV3Criteria  : 12개 binary 체크 기준 클래스
    evaluate             : 통합 검증 실행
    EvaluationResult     : 결과 구조체
    CheckResult          : 개별 체크 결과
"""
from __future__ import annotations

from .criteria import EVAL, EVAL_V3, EvaluatorV3Criteria
from .run import CheckResult, EvaluationResult, evaluate

__all__ = [
    "EVAL",
    "EVAL_V3",
    "EvaluatorV3Criteria",
    "CheckResult",
    "EvaluationResult",
    "evaluate",
]
