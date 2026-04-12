"""CUFA Evaluator v3 — 실행가능성(Actionability) 검증 기준 레지스트리.

v2(분량/문체 기반) → v3(실행가능성 binary 기반) 전환.

12개 binary 체크: 분량 카운팅 없음, SMIC 문체 강제 없음.
"이걸 빼면 투자 판단에 지장이 있는가?" 질문만 남긴다.

SKILL.md §1.2 / §8 구현체.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvaluatorV3Criteria:
    """Evaluator v3 — 12개 실행가능성 binary 체크.

    각 필드가 True이면 해당 항목을 보고서에서 반드시 확인.
    KILL_CONDITIONS_MIN / CATALYST_MIN 만 숫자 임계값.

    참조 스탯(할루시네이션 패턴)은 PASS/FAIL 아님 — 경고만.
    """

    # ── 1. 투자의견 ──────────────────────────────────────────────────────
    REQUIRE_OPINION: bool = True
    """BUY / HOLD / SELL / WATCH / AVOID 중 하나 명시."""

    # ── 2. 목표주가 ──────────────────────────────────────────────────────
    REQUIRE_TARGET_PRICE: bool = True
    """숫자로 된 목표주가. "~원" 또는 Trade Ticket에 target_price."""

    # ── 3. 손절가 ────────────────────────────────────────────────────────
    REQUIRE_STOP_LOSS: bool = True
    """명시적 손절가(stop_loss). 없으면 리스크 관리 불가."""

    # ── 4. 포지션 비중 ───────────────────────────────────────────────────
    REQUIRE_POSITION_SIZE: bool = True
    """position_size_pct (%) — 포트폴리오 내 비중."""

    # ── 5. Bear Case / 최소 하방 ─────────────────────────────────────────
    REQUIRE_BEAR_FLOOR: bool = True
    """Bear 시나리오 가격 또는 하방 한계 제시."""

    # ── 6. Kill Conditions (최소 개수) ───────────────────────────────────
    REQUIRE_KILL_CONDITIONS_MIN: int = 3
    """투자 논리를 무효화하는 Kill Condition 최소 개수."""

    # ── 7. Catalyst Timeline (최소 개수) ─────────────────────────────────
    REQUIRE_CATALYST_TIMELINE_MIN: int = 3
    """날짜 붙은 Catalyst 이벤트 최소 개수."""

    # ── 8. Trade Ticket YAML ─────────────────────────────────────────────
    REQUIRE_TRADE_TICKET: bool = True
    """trade_ticket.yaml 또는 HTML 내 Trade Ticket 블록 파싱 가능 여부."""

    # ── 9. 데이터 출처 ───────────────────────────────────────────────────
    REQUIRE_DATA_SOURCES: bool = True
    """데이터 출처 1건 이상 (DART / KRX / ECOS / Nexus MCP 등)."""

    # ── 10. Backtest Hook ─────────────────────────────────────────────────
    REQUIRE_BACKTEST_HOOK: bool = True
    """backtest_engine 필드 또는 QuantPipeline 연동 주석."""

    # ── 11. Falsifiable Thesis ────────────────────────────────────────────
    REQUIRE_FALSIFIABLE_THESIS: bool = True
    """"이 가정이 틀리면 매도" 반증 조건 최소 1건."""

    # ── 12. Risk/Reward Ratio ─────────────────────────────────────────────
    REQUIRE_RISK_REWARD: bool = True
    """Risk/Reward 수치 명시 (예: 1.42x)."""

    # ── 참조 스탯 (PASS/FAIL 아님 — 경고) ───────────────────────────────
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


#: 기본 Evaluator v3 기준 인스턴스.
EVAL_V3: EvaluatorV3Criteria = EvaluatorV3Criteria()

# v2 하위호환 alias (이전 코드가 EVAL을 직접 참조하는 경우)
EVAL = EVAL_V3
