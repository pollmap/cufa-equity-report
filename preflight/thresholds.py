"""CUFA Preflight — 표준 임계값 레지스트리.

모든 종목에 동일하게 적용되는 상수. 종목별 오버라이드가 필요하면
`PreflightThresholds`를 상속하여 frozen dataclass로 재정의한다.

예시:
    @dataclass(frozen=True)
    class BioPreflightThresholds(PreflightThresholds):
        MIN_YEARS_ACTUAL: int = 2  # 신생 바이오는 3년 실적 없을 수 있음
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PreflightThresholds:
    """CUFA Phase 0 표준 임계값.

    모든 값은 정량 기준이며 SKILL.md §1.1의 정의와 일치한다.
    """

    # === 재무 검증 ===
    FINANCIAL_DRIFT_MAX: float = 0.10
    """빌더 하드코딩 재무 수치와 MCP 실데이터의 허용 괴리 (10%)."""

    OP_INCOME_SIGN_CHECK: bool = True
    """영업손익의 부호 반전 시 무조건 STOP (Kitchen Sinking vs 실적 악화 판정 필요)."""

    # === 주가 검증 ===
    PRICE_DRIFT_MAX: float = 0.10
    """빌더 현재가와 실주가의 허용 괴리 (10%)."""

    VOLATILITY_RERATING_TRIGGER: float = 0.30
    """1년 수익률 절대값이 이 값을 초과하면 Re-rating v2 모드로 전환."""

    # === 삼각검증 ===
    SELF_CONSISTENCY_TOLERANCE: float = 0.01
    """PBR × BPS = Price 의 자체 정합성 허용 오차 (1%)."""

    # === 데이터 품질 ===
    MIN_YEARS_ACTUAL: int = 3
    """최소 실적 연도 수."""

    MIN_DAYS_OHLCV: int = 200
    """1년 주가 수집 시 최소 거래일 수."""

    REQUIRE_RAW_ARCHIVE: bool = True
    """data/raw/ 원본 응답 파일 보존 필수 여부."""


#: 기본 임계값 인스턴스 — 종목별 오버라이드가 없는 한 이것을 사용.
PREFLIGHT: PreflightThresholds = PreflightThresholds()
