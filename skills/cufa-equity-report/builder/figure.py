"""CUFA Builder — 도표 번호 카운터.

섹션별로 1부터 시작하는 "도표 X-Y" 번호를 부여한다.
여러 보고서를 한 프로세스에서 빌드할 때 충돌 방지를 위해 클래스로 분리.
SKILL.md §6.2 구현체.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FigureCounter:
    """섹션별 도표 번호 카운터.

    빌드 시작 시 `reset()` 을 호출하여 초기화한다. 서브에이전트 병렬 빌드 시
    각 에이전트가 별도 인스턴스를 사용해 상호 간섭을 방지한다.
    """

    _counters: dict[int, int] = field(default_factory=dict)

    def next(self, sec: int) -> str:
        """섹션 `sec` 의 다음 도표 번호를 반환 (`"3-2"` 형식)."""
        self._counters[sec] = self._counters.get(sec, 0) + 1
        return f"{sec}-{self._counters[sec]}"

    def reset(self) -> None:
        self._counters.clear()


#: 모듈 기본 인스턴스. 대부분의 종목 빌드는 이것을 공유한다.
DEFAULT_COUNTER = FigureCounter()


def fig_num(sec: int) -> str:
    """섹션 `sec` 의 다음 도표 번호 (기본 카운터 기준)."""
    if sec <= 0:
        return ""
    return DEFAULT_COUNTER.next(sec)


def reset_figures() -> None:
    """기본 카운터를 초기화. 새 빌드 시작 전 호출."""
    DEFAULT_COUNTER.reset()
