"""CUFA Post-processing — 보호-치환-복원 패턴.

광범위 수치 치환 시 v1 참조 블록(Re-rating Note, Phase 6.5, Cover)을
보호한 후 본문만 치환, 다시 복원. SKILL.md §29-3b + §30-0 구현체.

**핵심 규칙**:
- 단독 숫자(`'45,000원'` 등) 치환 금지 — 반드시 고유 리터럴만.
- 치환 대상이 v1 참조 문구에도 등장하면 보호 영역에 포함.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

MARKER_START = "\uE100"  # Private Use Area
MARKER_END = "\uE101"


@dataclass(frozen=True)
class ReplaceRule:
    """단일 치환 규칙."""

    old: str
    new: str
    description: str = ""


@dataclass(frozen=True)
class ProtectedReplaceConfig:
    """보호-치환-복원 설정.

    Attributes:
        protect_patterns: 치환에서 제외할 HTML 영역 정규식 (DOTALL).
        rules: ReplaceRule 튜플 — 고유 리터럴만 허용.
    """

    protect_patterns: tuple[str, ...] = field(
        default_factory=lambda: (
            # Re-rating v2 섹션 전체
            r'<div class="section" id="rerating_v2".*?(?=<div class="section"|<div class="footer")',
            # Phase 6.5 백테스트 블록
            r'<div class="section" id="phase65".*?(?=<div class="section"|<div class="footer")',
            # Cover 블록 (직접 편집으로 v2 반영됨)
            r'<div class="cover">.*?(?=<div class="section")',
        )
    )
    rules: tuple[ReplaceRule, ...] = ()


def protected_replace(html: str, config: ProtectedReplaceConfig) -> str:
    """보호 영역을 제외하고 치환 적용.

    1) 보호 영역을 `\uE100N\uE101` 마커로 임시 치환
    2) 본문에만 규칙 적용
    3) 마커를 원본으로 복원

    Args:
        html: 원본 HTML.
        config: 보호 패턴 + 치환 규칙.

    Returns:
        치환된 HTML.
    """
    protected: list[str] = []

    def _protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"{MARKER_START}{len(protected) - 1}{MARKER_END}"

    # 1) 보호 영역 마킹
    for pattern in config.protect_patterns:
        html = re.sub(pattern, _protect, html, flags=re.DOTALL)

    # 2) 치환 규칙 적용
    for rule in config.rules:
        html = html.replace(rule.old, rule.new)

    # 3) 복원
    def _restore(match: re.Match[str]) -> str:
        return protected[int(match.group(1))]

    return re.sub(
        f"{MARKER_START}(\\d+){MARKER_END}",
        _restore,
        html,
    )
