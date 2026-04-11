"""CUFA Preflight — DART 응답 표준 파서.

`dart_financial_statements` 응답의 연결(CFS) / 별도(OFS) 혼재를 안전하게 분리.
SKILL.md §10.3 구현체.
"""
from __future__ import annotations

from typing import Any, Iterable


def split_cfs_ofs(items: Iterable[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    """DART 응답 rows를 연결/별도로 분리.

    DART는 한 번의 호출에 CFS+OFS를 함께 반환하며, 같은 `sj_div` 안에
    연결이 앞쪽 ord, 별도가 뒤쪽 ord로 섞여 있다. `ord` 기준 정렬 후
    중간을 기준으로 분할한다.

    Args:
        items: 원본 row 리스트.

    Returns:
        `(cfs_rows, ofs_rows)` 튜플.
    """
    rows = list(items)
    cfs: list[dict] = []
    ofs: list[dict] = []

    for sj in ("IS", "BS", "CF"):
        subset = sorted(
            [r for r in rows if r.get("sj_div") == sj],
            key=lambda r: int(r.get("ord", 0)),
        )
        if not subset:
            continue

        # 동일 계정명이 두 번 등장하면 1세트 크기를 파악해서 분할
        seen: dict[str, int] = {}
        split_idx = len(subset)
        for idx, r in enumerate(subset):
            name = r.get("account_nm", "")
            if name in seen:
                split_idx = idx
                break
            seen[name] = idx

        cfs.extend(subset[:split_idx])
        ofs.extend(subset[split_idx:])

    return cfs, ofs


def get_account_value(
    rows: Iterable[dict[str, Any]],
    account_name: str,
    period: str = "thstrm",
) -> int:
    """계정명으로 값 추출 (정수, 원 단위).

    Args:
        rows: DART row 리스트.
        account_name: 계정 이름 (예: "매출액", "영업이익").
        period: "thstrm"(당기) / "frmtrm"(전기) / "bfefrmtrm"(전전기).

    Returns:
        금액 (원 단위, 미발견 시 0).
    """
    field = f"{period}_amount"
    for row in rows:
        if row.get("account_nm") == account_name:
            raw = str(row.get(field, "0")).replace(",", "").strip()
            if not raw or raw == "-":
                return 0
            try:
                return int(raw)
            except ValueError:
                return 0
    return 0


def get_is_summary(cfs_rows: list[dict]) -> dict[str, int]:
    """연결 IS에서 핵심 지표 추출 (매출/영업이익/순이익)."""
    return {
        "revenue": get_account_value(cfs_rows, "매출액"),
        "op_income": get_account_value(cfs_rows, "영업이익"),
        "net_income": get_account_value(cfs_rows, "당기순이익(손실)"),
    }
