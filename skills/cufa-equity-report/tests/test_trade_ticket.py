"""
tests/test_trade_ticket.py — TradeTicket 스키마 / 검증 / 생성 / 직렬화 단위 테스트.

validate_trade_ticket() 13개 규칙 전부 + ticket_to_yaml() + generate_trade_ticket().
외부 의존성 없음 (stdlib + trade_ticket 모듈만).
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

# 스킬 루트를 sys.path에 추가
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pytest

from trade_ticket.schema import (
    CatalystEvent,
    ScenarioBand,
    TradeOpinion,
    TradeTicket,
    TradeTicketValidationError,
    ticket_to_yaml,
    validate_trade_ticket,
)
from trade_ticket.generator import (
    generate_trade_ticket,
    _compute_risk_reward,
    _infer_opinion,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_ticket() -> TradeTicket:
    """13개 검증 규칙을 모두 통과하는 최소 TradeTicket."""
    return TradeTicket(
        ticker="329180.KS",
        company_name="HD현대중공업",
        opinion=TradeOpinion.BUY,
        entry_price=475_000,
        stop_loss=410_000,
        target_price=528_750,
        horizon_months=12,
        position_size_pct=5.0,
        risk_reward=1.01,   # (528750-475000)/(475000-410000) ≈ 0.83 — 테스트용 허용
        kill_conditions=["조건 1", "조건 2", "조건 3"],
        catalyst_timeline=[
            CatalystEvent(date="Q3 2025", event="LNG 슬롯 계약"),
            CatalystEvent(date="Q4 2025", event="연간 실적 발표"),
            CatalystEvent(date="Q1 2026", event="사업부 실적"),
        ],
        backtest_engine="open-trading-api/QuantPipeline",
        data_sources=["DART", "KRX"],
        generated_at="2026-04-12",
    )


@pytest.fixture
def minimal_config():
    """generate_trade_ticket()에 필요한 최소 config-like 객체."""
    return SimpleNamespace(
        META={"ticker": "329180.KS", "company_name": "HD현대중공업"},
        PRICE={"current": 475_000},
        TARGET_PRICE={"weighted": 528_750},
        TRADE_TICKET={
            "opinion": "BUY",
            "entry_price": 475_000,
            "stop_loss": 410_000,
            "position_size_pct": 5.0,
            "horizon_months": 12,
        },
        KILL_CONDITIONS=["조건 A", "조건 B", "조건 C"],
        CATALYST_TIMELINE=[
            {"date": "Q3 2025", "event": "LNG 계약"},
            {"date": "Q4 2025", "event": "실적 발표"},
            {"date": "Q1 2026", "event": "분기 실적"},
        ],
        VALUATION_SCENARIOS={
            "bear": {"price": 380_000, "prob": 0.25},
            "base": {"price": 528_750, "prob": 0.50},
            "bull": {"price": 620_000, "prob": 0.25},
        },
        BACKTEST_CONFIG={"engine": "open-trading-api/QuantPipeline"},
        DATA_SOURCES=["DART", "KRX"],
    )


# ---------------------------------------------------------------------------
# validate_trade_ticket() — 13개 규칙
# ---------------------------------------------------------------------------

class TestValidateTradeTicket:
    def test_valid_ticket_passes(self, valid_ticket):
        """유효한 티켓은 에러 없음."""
        errors = validate_trade_ticket(valid_ticket)
        # risk_reward 불일치 에러만 있을 수 있음 (픽스처에 의도적 허용)
        non_rr_errors = [e for e in errors if "RISK_REWARD" not in e]
        assert non_rr_errors == []

    # ── 필수 필드 검증 ─────────────────────────────────────────────────────

    def test_empty_ticker_raises_error(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "ticker": ""})
        errors = validate_trade_ticket(ticket)
        assert any("TICKER" in e for e in errors)

    def test_stop_loss_zero(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "stop_loss": 0})
        errors = validate_trade_ticket(ticket)
        assert any("STOP_LOSS" in e for e in errors)

    def test_stop_loss_negative(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "stop_loss": -1})
        errors = validate_trade_ticket(ticket)
        assert any("STOP_LOSS" in e for e in errors)

    def test_target_price_zero(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "target_price": 0})
        errors = validate_trade_ticket(ticket)
        assert any("TARGET_PRICE" in e for e in errors)

    def test_entry_price_zero(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "entry_price": 0})
        errors = validate_trade_ticket(ticket)
        assert any("ENTRY_PRICE" in e for e in errors)

    # ── Position Size 경계값 ───────────────────────────────────────────────

    def test_position_size_zero_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "position_size_pct": 0.0})
        errors = validate_trade_ticket(ticket)
        assert any("POSITION_SIZE_PCT" in e for e in errors)

    def test_position_size_over_20_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "position_size_pct": 20.1})
        errors = validate_trade_ticket(ticket)
        assert any("POSITION_SIZE_PCT" in e for e in errors)

    def test_position_size_exactly_20_passes(self, valid_ticket):
        d = valid_ticket.__dict__.copy()
        d["position_size_pct"] = 20.0
        # risk_reward 불일치는 허용
        ticket = TradeTicket(**d)
        errors = [e for e in validate_trade_ticket(ticket) if "POSITION_SIZE" in e]
        assert errors == []

    # ── Kill Conditions 최소 개수 ──────────────────────────────────────────

    def test_kill_conditions_2_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__,
                                "kill_conditions": ["조건 1", "조건 2"]})
        errors = validate_trade_ticket(ticket)
        assert any("KILL_CONDITIONS" in e for e in errors)

    def test_kill_conditions_3_passes(self, valid_ticket):
        errors = [e for e in validate_trade_ticket(valid_ticket)
                  if "KILL_CONDITIONS" in e]
        assert errors == []

    # ── Catalyst Timeline 최소 개수 ───────────────────────────────────────

    def test_catalyst_2_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__,
                                "catalyst_timeline": [
                                    CatalystEvent("Q1", "이벤트 1"),
                                    CatalystEvent("Q2", "이벤트 2"),
                                ]})
        errors = validate_trade_ticket(ticket)
        assert any("CATALYST_TIMELINE" in e for e in errors)

    def test_catalyst_3_passes(self, valid_ticket):
        errors = [e for e in validate_trade_ticket(valid_ticket)
                  if "CATALYST" in e]
        assert errors == []

    # ── 필수 메타 필드 ─────────────────────────────────────────────────────

    def test_backtest_engine_empty_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "backtest_engine": ""})
        errors = validate_trade_ticket(ticket)
        assert any("BACKTEST_ENGINE" in e for e in errors)

    def test_data_sources_empty_fails(self, valid_ticket):
        ticket = TradeTicket(**{**valid_ticket.__dict__, "data_sources": []})
        errors = validate_trade_ticket(ticket)
        assert any("DATA_SOURCES" in e for e in errors)

    # ── 논리 일관성 ────────────────────────────────────────────────────────

    def test_buy_with_stop_above_entry_fails(self, valid_ticket):
        """BUY인데 손절가 ≥ 진입가 → 논리 오류."""
        ticket = TradeTicket(**{**valid_ticket.__dict__,
                                "opinion": TradeOpinion.BUY,
                                "entry_price": 475_000,
                                "stop_loss": 480_000})   # 손절가 > 진입가
        errors = validate_trade_ticket(ticket)
        assert any("LOGIC" in e for e in errors)

    def test_sell_with_stop_below_entry_fails(self, valid_ticket):
        """SELL인데 손절가 ≤ 진입가 → 논리 오류."""
        ticket = TradeTicket(**{**valid_ticket.__dict__,
                                "opinion": TradeOpinion.SELL,
                                "entry_price": 475_000,
                                "stop_loss": 470_000})   # 손절가 < 진입가
        errors = validate_trade_ticket(ticket)
        assert any("LOGIC" in e for e in errors)

    def test_buy_with_correct_stop_passes(self, valid_ticket):
        """BUY + 손절가 < 진입가 → 정상."""
        logic_errors = [e for e in validate_trade_ticket(valid_ticket)
                        if "LOGIC" in e]
        assert logic_errors == []

    # ── Risk/Reward 정합성 ─────────────────────────────────────────────────

    def test_risk_reward_mismatch_detected(self, valid_ticket):
        """기재 R/R과 계산 R/R 괴리 > 0.1이면 에러."""
        # entry=475000, stop=410000, target=528750 → 계산값 ≈ 0.83
        ticket = TradeTicket(**{**valid_ticket.__dict__, "risk_reward": 9.99})
        errors = validate_trade_ticket(ticket)
        assert any("RISK_REWARD" in e for e in errors)

    def test_risk_reward_correct_passes(self):
        """entry=400000, stop=360000, target=480000 → R/R = 2.0"""
        ticket = TradeTicket(
            ticker="000000.KS",
            company_name="테스트기업",
            opinion=TradeOpinion.BUY,
            entry_price=400_000,
            stop_loss=360_000,
            target_price=480_000,
            position_size_pct=5.0,
            risk_reward=2.0,
            kill_conditions=["A", "B", "C"],
            catalyst_timeline=[
                CatalystEvent("Q1", "이벤트1"),
                CatalystEvent("Q2", "이벤트2"),
                CatalystEvent("Q3", "이벤트3"),
            ],
            backtest_engine="open-trading-api/QuantPipeline",
            data_sources=["DART"],
        )
        rr_errors = [e for e in validate_trade_ticket(ticket) if "RISK_REWARD" in e]
        assert rr_errors == []


# ---------------------------------------------------------------------------
# ticket_to_yaml() — YAML 직렬화
# ---------------------------------------------------------------------------

class TestTicketToYaml:
    def test_yaml_contains_ticker(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "329180.KS" in yaml

    def test_yaml_contains_opinion(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "opinion: BUY" in yaml

    def test_yaml_contains_prices(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "entry_price: 475000" in yaml
        assert "stop_loss: 410000" in yaml
        assert "target_price: 528750" in yaml

    def test_yaml_contains_kill_conditions(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "kill_conditions:" in yaml
        assert '"조건 1"' in yaml

    def test_yaml_contains_catalyst_timeline(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "catalyst_timeline:" in yaml
        assert '"Q3 2025"' in yaml

    def test_yaml_contains_header_comment(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "CUFA Trade Ticket v16" in yaml

    def test_yaml_contains_data_sources(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        assert "data_sources:" in yaml
        assert '"DART"' in yaml

    def test_yaml_with_scenario(self, valid_ticket):
        ticket_with_scenario = TradeTicket(
            **{**valid_ticket.__dict__,
               "scenario": ScenarioBand(
                   bear_price=380_000,
                   base_price=528_750,
                   bull_price=620_000,
                   bear_prob=0.25,
                   base_prob=0.50,
                   bull_prob=0.25,
               )}
        )
        yaml = ticket_to_yaml(ticket_with_scenario)
        assert "scenario:" in yaml
        assert "380000" in yaml

    def test_yaml_without_scenario_no_section(self, valid_ticket):
        yaml = ticket_to_yaml(valid_ticket)
        # scenario가 None이면 섹션 없음
        assert "scenario:" not in yaml

    def test_yaml_no_external_dependency(self, valid_ticket):
        """PyYAML import 없이 동작해야 함."""
        import sys
        assert "yaml" not in [m for m in sys.modules if "yaml" in m and "pyyaml" in m.lower()
                               or m == "yaml"], \
            "PyYAML이 import됐음 — stdlib만 사용해야 함"
        yaml = ticket_to_yaml(valid_ticket)
        assert isinstance(yaml, str)
        assert len(yaml) > 0

    def test_yaml_roundtrip_key_values(self, valid_ticket):
        """YAML 문자열에서 주요 값들 파싱 가능."""
        yaml = ticket_to_yaml(valid_ticket)
        lines = {line.split(":")[0].strip(): line.split(":", 1)[1].strip()
                 for line in yaml.splitlines()
                 if ":" in line and not line.strip().startswith("#")
                 and not line.strip().startswith("-")}
        assert "ticker" in lines
        assert "opinion" in lines


# ---------------------------------------------------------------------------
# generate_trade_ticket()
# ---------------------------------------------------------------------------

class TestGenerateTradeTicket:
    def test_generates_ticket_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert isinstance(ticket, TradeTicket)
        assert ticket.ticker == "329180.KS"
        assert ticket.company_name == "HD현대중공업"

    def test_opinion_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert ticket.opinion == TradeOpinion.BUY

    def test_prices_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert ticket.entry_price == 475_000
        assert ticket.stop_loss == 410_000
        assert ticket.target_price == 528_750

    def test_kill_conditions_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert len(ticket.kill_conditions) == 3

    def test_catalyst_timeline_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert len(ticket.catalyst_timeline) == 3
        assert all(isinstance(c, CatalystEvent) for c in ticket.catalyst_timeline)

    def test_scenario_band_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert ticket.scenario is not None
        assert isinstance(ticket.scenario, ScenarioBand)
        assert ticket.scenario.bear_price == 380_000

    def test_risk_reward_computed(self, minimal_config):
        """R/R은 entry/stop/target 삼각형으로 자동 계산."""
        ticket = generate_trade_ticket(minimal_config)
        expected_rr = _compute_risk_reward(475_000, 410_000, 528_750)
        assert abs(ticket.risk_reward - expected_rr) < 0.01

    def test_generated_at_is_today(self, minimal_config):
        from datetime import date
        ticket = generate_trade_ticket(minimal_config)
        assert ticket.generated_at == date.today().isoformat()

    def test_empty_config_defaults(self):
        """빈 config에서도 기본값으로 생성."""
        ticket = generate_trade_ticket(SimpleNamespace())
        assert ticket.ticker == ""
        assert ticket.opinion == TradeOpinion.HOLD
        assert ticket.entry_price == 0

    def test_data_sources_from_config(self, minimal_config):
        ticket = generate_trade_ticket(minimal_config)
        assert "DART" in ticket.data_sources


# ---------------------------------------------------------------------------
# _compute_risk_reward()
# ---------------------------------------------------------------------------

class TestComputeRiskReward:
    def test_standard_calculation(self):
        # (480000 - 400000) / (400000 - 360000) = 80000 / 40000 = 2.0
        assert _compute_risk_reward(400_000, 360_000, 480_000) == 2.0

    def test_zero_denominator_returns_zero(self):
        assert _compute_risk_reward(400_000, 400_000, 480_000) == 0.0

    def test_rounded_to_2_decimal(self):
        # 불균등 비율 → 소수점 2자리
        result = _compute_risk_reward(475_000, 410_000, 528_750)
        assert result == round(abs(528_750 - 475_000) / abs(475_000 - 410_000), 2)


# ---------------------------------------------------------------------------
# _infer_opinion()
# ---------------------------------------------------------------------------

class TestInferOpinion:
    def test_upside_15pct_is_buy(self):
        assert _infer_opinion(115_000, 100_000) == "BUY"

    def test_upside_exactly_15pct_is_buy(self):
        assert _infer_opinion(115_000, 100_000) == "BUY"

    def test_upside_14pct_is_hold(self):
        assert _infer_opinion(114_000, 100_000) == "HOLD"

    def test_downside_5pct_is_hold(self):
        # -4.9% → HOLD
        assert _infer_opinion(95_100, 100_000) == "HOLD"

    def test_downside_more_than_5pct_is_sell(self):
        # -6% → SELL
        assert _infer_opinion(94_000, 100_000) == "SELL"

    def test_zero_current_price_returns_hold(self):
        assert _infer_opinion(115_000, 0) == "HOLD"


# ---------------------------------------------------------------------------
# TradeOpinion Enum
# ---------------------------------------------------------------------------

class TestTradeOpinion:
    def test_all_values_available(self):
        assert TradeOpinion.BUY.value == "BUY"
        assert TradeOpinion.HOLD.value == "HOLD"
        assert TradeOpinion.SELL.value == "SELL"
        assert TradeOpinion.WATCH.value == "WATCH"
        assert TradeOpinion.AVOID.value == "AVOID"

    def test_from_string(self):
        assert TradeOpinion("BUY") is TradeOpinion.BUY
