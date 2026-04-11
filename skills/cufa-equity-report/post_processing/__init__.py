"""CUFA Post-processing — 빌드 후 HTML 처리 모듈.

공개 API:
    smic_inject              : SMIC 문체(동사/본서는/전술한) 주입
    protected_replace        : 보호-치환-복원 수치 치환
    ProtectedReplaceConfig   : 치환 규칙 설정
"""
from __future__ import annotations

from .smic_injector import smic_inject
from .protect_replace import (
    ProtectedReplaceConfig,
    ReplaceRule,
    protected_replace,
)

__all__ = [
    "smic_inject",
    "protected_replace",
    "ProtectedReplaceConfig",
    "ReplaceRule",
]
