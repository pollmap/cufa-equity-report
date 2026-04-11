"""CUFA Post-processing — SMIC 문체 주입.

본문에 '동사/본서는/전술한' 패턴을 주입하여 CUFA SMIC_STYLE Evaluator 기준을
충족시킨다. SKILL.md §5 구현체.

**원칙**: 본문은 `<div class="content-area">` 안쪽만 대상. Cover/TOC/Header는 보호.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

MARKER_START = "\uE110"
MARKER_END = "\uE111"


@dataclass(frozen=True)
class SMICInjectConfig:
    """SMIC 문체 주입 설정."""

    #: 보호 영역 정규식 (Cover/TOC/Header/Footer 등).
    protect_patterns: tuple[str, ...] = field(
        default_factory=lambda: (
            r"<title>[^<]*</title>",
            r'class="cover-company"[^>]*>[^<]*',
            r'class="sb-name"[^>]*>[^<]*',
            r'class="section-subheader"[^>]*>[^<]*',
            r'class="section-title"[^>]*>[^<]*',
            r'<div class="author">[^<]*',
            r'<div class="org">[^<]*',
            r'<a href="#[^"]*"[^>]*>[^<]*',
        )
    )

    #: '{기업명}' → '동사' 치환 조사 리스트. 첫 등장 1회는 별도 제외.
    postpositions: tuple[str, ...] = field(
        default_factory=lambda: (
            "이", "가", "은", "는", "의", "을", "를",
            "에", "에서", "와", "과", "도",
        )
    )


def smic_inject(
    html: str,
    company_name: str,
    config: SMICInjectConfig | None = None,
) -> str:
    """본문의 기업명을 '동사'로 일괄 치환 (보호 영역 제외).

    Args:
        html: 원본 HTML.
        company_name: 분석 대상 기업명 (예: "현대건설").
        config: 보호 패턴 설정 (기본값 사용 권장).

    Returns:
        '동사' 주입된 HTML.
    """
    if config is None:
        config = SMICInjectConfig()

    protected: list[str] = []

    def _protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"{MARKER_START}{len(protected) - 1}{MARKER_END}"

    # 1) 보호 영역 마킹
    for pattern in config.protect_patterns:
        html = re.sub(pattern, _protect, html)

    # 2) '{기업명}{조사}' → '동사{조사}' 치환
    for postposition in config.postpositions:
        old = f"{company_name}{postposition}"
        new = f"동사{_convert_postposition(postposition)}"
        html = html.replace(old, new)

    # 기업명 단독 (괄호, 문장 끝 등) 치환은 의도적으로 건드리지 않음
    # → 첫 등장 문장과 제목에서만 남고 본문은 조사 있는 형태가 대부분

    # 3) 복원
    def _restore(match: re.Match[str]) -> str:
        return protected[int(match.group(1))]

    return re.sub(
        f"{MARKER_START}(\\d+){MARKER_END}",
        _restore,
        html,
    )


def _convert_postposition(postposition: str) -> str:
    """'동사' 뒤에 오는 조사는 '사'(자음)에 맞춰 조정.

    '이→가', '은→는', '을→를', '과→와' 등.
    """
    conversion = {
        "이": "가",  # 자음 → 모음
        "은": "는",
        "을": "를",
        "과": "와",
    }
    return conversion.get(postposition, postposition)
