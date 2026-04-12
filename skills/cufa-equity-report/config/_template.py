"""CUFA 종목 Config 템플릿 (v16.0 표준).

새 종목 작성 시 이 파일을 `config/{stock_code}.py`로 복사하여
종목별 값만 교체한다. 임계값·규칙은 절대 여기에 하드코딩하지 말고
`preflight.thresholds.PREFLIGHT` 를 사용한다.

v16 추가 필드:
  TRADE_TICKET      — Trade Ticket 파라미터 (stop_loss, position_size_pct 등)
  KILL_CONDITIONS   — 투자 논리 무효화 조건 목록 (최소 3개)
  BACKTEST_CONFIG   — open-trading-api/QuantPipeline 설정
  FEEDBACK_LOOP     — Phase 7 복기 설정
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from preflight import PREFLIGHT, PreflightThresholds

KST = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class StockConfig:
    """종목별 설정 — 데이터만 들고 있음. 로직 없음.

    표준 임계값 오버라이드가 필요하면 `thresholds` 필드에
    `PreflightThresholds` 서브클래스 인스턴스를 주입.
    """

    # === 종목 식별 ===
    stock_code: str                  # "000720"
    company_name: str                # "현대건설"
    company_name_en: str              # "Hyundai E&C"
    market: str                      # "KOSPI" / "KOSDAQ"
    industry: str                    # "건설" (INDUSTRY_CHECKLIST 키)
    subtitle: str                    # 보고서 부제/캐치프레이즈

    # === 빌더 입력 수치 (Pre-flight 대상) ===
    builder_revenue: float           # 기준 연도 매출
    builder_op_income: float         # 기준 연도 영업이익
    builder_price: float             # 빌더 기준 현재가
    builder_bps: float               # 빌더 기준 BPS
    builder_eps_next: float          # 2026E EPS
    shares_outstanding: float        # 발행주식수

    # === 리포트 메타 ===
    target_year: int                 # 기준 연도 (최근 확정 실적)
    report_date: datetime = field(default_factory=lambda: datetime.now(KST))
    data_dir: Path = field(default_factory=lambda: Path("data/raw"))
    output_dir: Path = field(default_factory=lambda: Path("output"))

    # === 팀 ===
    team_name: str = "CUFA"
    team_members: tuple[str, ...] = ()

    # === Peer (종목명 → 티커) ===
    peers_kr: dict[str, str] = field(default_factory=dict)
    peers_global: dict[str, str] = field(default_factory=dict)

    # === 임계값 오버라이드 (선택) ===
    thresholds: PreflightThresholds = PREFLIGHT

    # === v16 Trade Ticket 파라미터 ===
    # generator.py가 이 필드를 읽어 Trade Ticket YAML을 생성한다.
    # 예: {"opinion": "BUY", "stop_loss": 410000, "position_size_pct": 5.0,
    #       "entry_price": 475000, "horizon_months": 12}
    trade_ticket: dict = field(default_factory=dict)

    # === v16 Kill Conditions (최소 3개 필수) ===
    # Evaluator v3 REQUIRE_KILL_CONDITIONS_MIN=3 기준.
    kill_conditions: tuple[str, ...] = ()

    # === v16 Backtest Config ===
    # open-trading-api/QuantPipeline에 전달되는 파라미터.
    # 예: {"engine": "open-trading-api/QuantPipeline",
    #       "benchmark": "KOSPI", "slippage_bps": 10}
    backtest_config: dict = field(default_factory=dict)

    # === v16 Feedback Loop (Phase 7) ===
    # 분기별 복기 설정.
    # 예: {"enabled": True, "review_cycle_months": 3,
    #       "output_dir": "data/feedback"}
    feedback_loop: dict = field(default_factory=dict)


# ─── 사용 예시 ───────────────────────────────────────────────────────
#
# # config/000720.py
# from config._template import StockConfig
#
# CONFIG = StockConfig(
#     stock_code="000720",
#     company_name="현대건설",
#     company_name_en="Hyundai E&C",
#     market="KOSPI",
#     industry="건설",
#     subtitle="중동 르네상스와 국내 재건축의 교차점",
#     builder_revenue=326_703 * 1e8,      # 32.67조 (DART 실데이터)
#     builder_op_income=-12_634 * 1e8,    # 2024 적자
#     builder_price=179_500,              # 실제 현재가
#     builder_bps=86_548,                 # DART 기준
#     builder_eps_next=11_635,            # 2026E
#     shares_outstanding=111_723_419,
#     target_year=2024,
#     team_name="CUFA 9기",
#     team_members=("이찬희",),
#     peers_kr={
#         "대우건설": "047040",
#         "DL이앤씨": "375500",
#         "GS건설": "006360",
#         "삼성물산": "028260",
#     },
#     peers_global={
#         "Vinci": "DG.PA",
#         "ACS": "ACS.MC",
#         "Kajima": "1812.T",
#         "Shimizu": "1803.T",
#     },
# )
