"""
CUFA Equity Report v2 — Components Library
SVG 차트 15종 + 테이블 + 레이아웃 + 고급 컴포넌트
HD건설기계 v4-1 클래스명 100% 호환
Python 3.10+ / 외부 의존성 없음
"""

from __future__ import annotations

import math
from typing import Sequence

# ============================================================
#  전역 설정
# ============================================================

# HD건설기계 표준 색상 (style.css :root)
C_PURPLE = "#7C6AF7"
C_PURPLE_LIGHT = "#A78BFA"
C_GREEN = "#00E09E"
C_RED = "#FF4D4D"
C_TEXT_SEC = "#A09CB0"
C_BORDER = "#2A2845"
C_DARK = "#1A1A2E"
C_CARD_BG = "#161628"

# SVG 기본
VB_W, VB_H = 700, 300
FONT = "'Noto Sans KR', sans-serif"

# 기본 팔레트 (6색 순환)
PALETTE = [C_PURPLE_LIGHT, C_GREEN, "#FFB84D", C_RED, "#4DC9F6", "#F77FBE"]

# 도표 카운터  sec -> count
_fig_counters: dict[int, int] = {}


def _reset_counters() -> None:
    """도표 카운터 초기화 (보고서 빌드 시작 시 호출)."""
    _fig_counters.clear()


def fig_num(sec: int = 0) -> str:
    """도표 번호 생성. sec=2 -> '도표 2-1.', '도표 2-2.' ..."""
    _fig_counters[sec] = _fig_counters.get(sec, 0) + 1
    return f"도표 {sec}-{_fig_counters[sec]}."


# ============================================================
#  내부 유틸
# ============================================================

def _esc(text: str) -> str:
    """HTML 이스케이프."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt(v: float | int, unit: str = "") -> str:
    """숫자 포맷 (천단위 콤마)."""
    if isinstance(v, float) and v != int(v):
        s = f"{v:,.1f}"
    else:
        s = f"{int(v):,}"
    return f"{s}{unit}"


def _neg_fmt(v: float | int) -> str:
    """음수: 빨간 괄호 표기."""
    if v < 0:
        return f'<span style="color:var(--red)">({_fmt(abs(v))})</span>'
    return _fmt(v)


def _pick_color(idx: int, colors: list[str] | None = None) -> str:
    if colors and idx < len(colors):
        return colors[idx]
    return PALETTE[idx % len(PALETTE)]


def _grid_lines(
    x_start: float,
    x_end: float,
    y_bottom: float,
    y_top: float,
    min_val: float,
    max_val: float,
    steps: int = 5,
) -> str:
    """Y축 그리드라인 + 라벨 SVG 생성."""
    if max_val == min_val:
        max_val = min_val + 1
    lines: list[str] = []
    for i in range(steps + 1):
        val = min_val + (max_val - min_val) * i / steps
        y = y_bottom - (y_bottom - y_top) * i / steps
        lines.append(
            f'<line x1="{x_start}" y1="{y:.1f}" x2="{x_end}" y2="{y:.1f}" '
            f'stroke="{C_BORDER}" stroke-width="0.5" stroke-dasharray="3,3"/>'
        )
        lines.append(
            f'<text x="{x_start - 6}" y="{y:.1f}" text-anchor="end" '
            f'font-size="10" fill="{C_TEXT_SEC}" '
            f'dominant-baseline="middle" font-family="{FONT}">'
            f"{_fmt(val)}</text>"
        )
    return "\n".join(lines)


def _chart_wrap(title: str, inner_svg: str, sec: int, w: int = VB_W, h: int = VB_H) -> str:
    """chart-box 래퍼 + 도표 번호."""
    fn = fig_num(sec) if sec else ""
    label = f"{fn} {_esc(title)}" if fn else _esc(title)
    return (
        f'<div class="chart-box">'
        f'<div class="chart-title">{label}</div>'
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;">\n{inner_svg}\n</svg></div>'
    )


# ============================================================
#  SVG 차트 15종
# ============================================================

def svg_bar(
    title: str,
    labels: Sequence[str],
    values: Sequence[float],
    colors: list[str] | None = None,
    show_line: Sequence[float] | None = None,
    sec: int = 0,
    unit: str = "",
) -> str:
    """수직 막대 차트. show_line: 선 오버레이 데이터."""
    n = len(labels)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 40
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    all_vals = list(values) + (list(show_line) if show_line else [])
    v_min = min(0, min(all_vals))
    v_max = max(all_vals) * 1.15

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    bar_w = min(area_w / n * 0.6, 50)
    gap = area_w / n

    for i, (lbl, val) in enumerate(zip(labels, values)):
        cx = margin_l + gap * (i + 0.5)
        ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
        h = ratio * area_h
        y = VB_H - margin_b - h
        c = _pick_color(i, colors)
        if val < 0:
            c = C_RED
        parts.append(
            f'<rect x="{cx - bar_w / 2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{h:.1f}" rx="3" fill="{c}" opacity="0.85"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_fmt(val, unit)}</text>"
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{VB_H - margin_b + 16:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_esc(str(lbl))}</text>"
        )

    if show_line:
        pts: list[str] = []
        for i, val in enumerate(show_line):
            cx = margin_l + gap * (i + 0.5)
            ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
            y = VB_H - margin_b - ratio * area_h
            pts.append(f"{cx:.1f},{y:.1f}")
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="{C_GREEN}" stroke-width="2" stroke-linejoin="round"/>'
        )
        for pt in pts:
            x, y = pt.split(",")
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="3" fill="{C_GREEN}"/>'
            )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_line(
    title: str,
    labels: Sequence[str],
    datasets: Sequence[tuple[str, Sequence[float], str]],
    sec: int = 0,
    unit: str = "",
) -> str:
    """라인 차트. datasets = [(name, values, color), ...]."""
    n = len(labels)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50

    all_vals = [v for _, vals, _ in datasets for v in vals]
    v_min = min(all_vals)
    v_max = max(all_vals)
    pad = (v_max - v_min) * 0.1 or 1
    v_min -= pad
    v_max += pad

    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    # X 라벨
    for i, lbl in enumerate(labels):
        x = margin_l + area_w * i / max(n - 1, 1)
        parts.append(
            f'<text x="{x:.1f}" y="{VB_H - margin_b + 18:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_esc(str(lbl))}</text>"
        )

    # 범례
    for di, (name, _, color) in enumerate(datasets):
        lx = margin_l + di * 110
        parts.append(
            f'<rect x="{lx}" y="{VB_H - 8}" width="10" height="3" rx="1" fill="{color}"/>'
            f'<text x="{lx + 14}" y="{VB_H - 4}" font-size="10" fill="{C_TEXT_SEC}" '
            f'font-family="{FONT}">{_esc(name)}</text>'
        )

    for name, vals, color in datasets:
        pts: list[str] = []
        for i, val in enumerate(vals):
            x = margin_l + area_w * i / max(n - 1, 1)
            ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
            y = VB_H - margin_b - ratio * area_h
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(
            f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
        )
        for pt in pts:
            x, y = pt.split(",")
            parts.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{color}"/>')

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_donut(
    title: str,
    segments: Sequence[tuple[str, float, str]],
    sec: int = 0,
) -> str:
    """도넛 차트. segments = [(label, value, color), ...]."""
    total = sum(v for _, v, _ in segments)
    if total <= 0:
        return ""

    cx, cy, r_outer, r_inner = 200, 150, 100, 55
    parts: list[str] = []
    angle = -90

    for label, val, color in segments:
        pct = val / total
        sweep = pct * 360
        end_angle = angle + sweep

        a1 = math.radians(angle)
        a2 = math.radians(end_angle)
        x1 = cx + r_outer * math.cos(a1)
        y1 = cy + r_outer * math.sin(a1)
        x2 = cx + r_outer * math.cos(a2)
        y2 = cy + r_outer * math.sin(a2)
        x3 = cx + r_inner * math.cos(a2)
        y3 = cy + r_inner * math.sin(a2)
        x4 = cx + r_inner * math.cos(a1)
        y4 = cy + r_inner * math.sin(a1)
        large = 1 if sweep > 180 else 0

        d = (
            f"M {x1:.1f} {y1:.1f} "
            f"A {r_outer} {r_outer} 0 {large} 1 {x2:.1f} {y2:.1f} "
            f"L {x3:.1f} {y3:.1f} "
            f"A {r_inner} {r_inner} 0 {large} 0 {x4:.1f} {y4:.1f} Z"
        )
        parts.append(f'<path d="{d}" fill="{color}" opacity="0.85"/>')
        angle = end_angle

    # 범례 (우측)
    lx = 360
    for i, (label, val, color) in enumerate(segments):
        ly = 60 + i * 28
        pct = val / total * 100
        parts.append(
            f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{color}"/>'
            f'<text x="{lx + 18}" y="{ly + 10}" font-size="11" fill="{C_TEXT_SEC}" '
            f'font-family="{FONT}">{_esc(label)} ({pct:.1f}%)</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_hbar(
    title: str,
    labels: Sequence[str],
    values: Sequence[float],
    sec: int = 0,
    unit: str = "",
) -> str:
    """수평 막대 차트."""
    n = len(labels)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 120, 60, 20, 20
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b
    bar_h = min(area_h / n * 0.6, 24)
    gap = area_h / n
    v_max = max(abs(v) for v in values) * 1.15

    parts: list[str] = []

    for i, (lbl, val) in enumerate(zip(labels, values)):
        cy = margin_t + gap * (i + 0.5)
        w = abs(val) / v_max * area_w if v_max else 0
        c = C_RED if val < 0 else C_PURPLE_LIGHT

        parts.append(
            f'<text x="{margin_l - 8}" y="{cy + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_esc(str(lbl))}</text>"
        )
        parts.append(
            f'<rect x="{margin_l}" y="{cy - bar_h / 2:.1f}" width="{w:.1f}" '
            f'height="{bar_h:.1f}" rx="3" fill="{c}" opacity="0.85"/>'
        )
        parts.append(
            f'<text x="{margin_l + w + 6:.1f}" y="{cy + 4:.1f}" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_fmt(val, unit)}</text>"
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_waterfall(
    title: str,
    items: Sequence[tuple[str, float]],
    sec: int = 0,
    unit: str = "",
) -> str:
    """폭포 차트. items = [(label, delta), ...]. 마지막 항목은 합계로 처리."""
    n = len(items)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 40
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b
    gap = area_w / n
    bar_w = min(gap * 0.6, 48)

    # 누적값 계산
    cumulative: list[float] = []
    running = 0.0
    for i, (_, delta) in enumerate(items):
        if i == n - 1:
            cumulative.append(running + delta)
        else:
            cumulative.append(running)
            running += delta

    all_vals = cumulative + [running]
    v_min = min(0, min(all_vals))
    v_max = max(all_vals) * 1.15

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    for i, (lbl, delta) in enumerate(items):
        cx = margin_l + gap * (i + 0.5)
        is_total = i == n - 1

        if is_total:
            total_val = cumulative[i]
            ratio = (total_val - v_min) / (v_max - v_min) if v_max != v_min else 0
            h = ratio * area_h
            y = VB_H - margin_b - h
            c = C_PURPLE
        else:
            base = cumulative[i]
            top = base + delta
            base_ratio = (base - v_min) / (v_max - v_min) if v_max != v_min else 0
            top_ratio = (top - v_min) / (v_max - v_min) if v_max != v_min else 0
            y_base = VB_H - margin_b - base_ratio * area_h
            y_top = VB_H - margin_b - top_ratio * area_h
            y = min(y_base, y_top)
            h = abs(y_base - y_top)
            c = C_GREEN if delta >= 0 else C_RED

        parts.append(
            f'<rect x="{cx - bar_w / 2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{max(h, 1):.1f}" rx="2" fill="{c}" opacity="0.85"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{"+" if delta > 0 and not is_total else ""}{_fmt(delta, unit)}</text>"
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{VB_H - margin_b + 16:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">'
            f"{_esc(str(lbl))}</text>"
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_scatter(
    title: str,
    points: Sequence[tuple[float, float, str]],
    sec: int = 0,
    x_label: str = "",
    y_label: str = "",
) -> str:
    """산점도. points = [(x, y, label), ...]."""
    if not points:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_pad = (x_max - x_min) * 0.1 or 1
    y_pad = (y_max - y_min) * 0.1 or 1
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, y_min, y_max))

    if x_label:
        parts.append(
            f'<text x="{VB_W / 2}" y="{VB_H - 4}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(x_label)}</text>'
        )
    if y_label:
        parts.append(
            f'<text x="14" y="{VB_H / 2}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}" '
            f'transform="rotate(-90,14,{VB_H / 2})">{_esc(y_label)}</text>'
        )

    for i, (px, py, lbl) in enumerate(points):
        sx = margin_l + (px - x_min) / (x_max - x_min) * area_w
        sy = VB_H - margin_b - (py - y_min) / (y_max - y_min) * area_h
        c = _pick_color(i)
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{c}" opacity="0.8"/>')
        parts.append(
            f'<text x="{sx:.1f}" y="{sy - 8:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(lbl)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_football(
    title: str,
    rows: Sequence[tuple[str, float, float, str]],
    current: float,
    sec: int = 0,
) -> str:
    """풋볼필드 밸류에이션. rows=[(method, low, high, color)], current=현재가."""
    if not rows:
        return ""

    all_vals = [v for _, lo, hi, _ in rows for v in (lo, hi)] + [current]
    v_min = min(all_vals) * 0.9
    v_max = max(all_vals) * 1.1

    margin_l, margin_r, margin_t, margin_b = 140, 30, 30, 20
    area_w = VB_W - margin_l - margin_r
    h = max(len(rows) * 40 + margin_t + margin_b, VB_H)
    bar_h = 14

    parts: list[str] = []

    def x_pos(val: float) -> float:
        return margin_l + (val - v_min) / (v_max - v_min) * area_w

    # 현재가 라인
    cx = x_pos(current)
    parts.append(
        f'<line x1="{cx:.1f}" y1="{margin_t - 10}" x2="{cx:.1f}" y2="{h - margin_b}" '
        f'stroke="{C_PURPLE}" stroke-width="2" stroke-dasharray="5,3"/>'
    )
    parts.append(
        f'<text x="{cx:.1f}" y="{margin_t - 14}" text-anchor="middle" '
        f'font-size="10" fill="{C_PURPLE}" font-family="{FONT}" font-weight="700">'
        f"현재가 {_fmt(current)}</text>"
    )

    for i, (method, lo, hi, color) in enumerate(rows):
        cy = margin_t + i * 40 + 20
        x1 = x_pos(lo)
        x2 = x_pos(hi)

        parts.append(
            f'<text x="{margin_l - 8}" y="{cy + 4}" text-anchor="end" '
            f'font-size="11" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(method)}</text>'
        )
        parts.append(
            f'<rect x="{x1:.1f}" y="{cy - bar_h / 2:.1f}" '
            f'width="{max(x2 - x1, 2):.1f}" height="{bar_h}" rx="4" '
            f'fill="{color}" opacity="0.7"/>'
        )
        parts.append(
            f'<text x="{x1 - 4:.1f}" y="{cy + 4}" text-anchor="end" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_fmt(lo)}</text>'
        )
        parts.append(
            f'<text x="{x2 + 4:.1f}" y="{cy + 4}" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_fmt(hi)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec, h=h)


def svg_heatmap(
    title: str,
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    data: Sequence[Sequence[float]],
    sec: int = 0,
    unit: str = "원",
) -> str:
    """히트맵. data[row][col]."""
    nr = len(row_labels)
    nc = len(col_labels)
    if nr == 0 or nc == 0:
        return ""

    margin_l, margin_t = 100, 40
    cell_w = min((VB_W - margin_l - 20) / nc, 80)
    cell_h = min((VB_H - margin_t - 20) / nr, 36)
    w = margin_l + cell_w * nc + 20
    h = margin_t + cell_h * nr + 20

    flat = [v for row in data for v in row]
    v_min, v_max = min(flat), max(flat)

    parts: list[str] = []

    # 열 헤더
    for j, cl in enumerate(col_labels):
        x = margin_l + cell_w * j + cell_w / 2
        parts.append(
            f'<text x="{x:.1f}" y="{margin_t - 10}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(cl)}</text>'
        )

    for i, rl in enumerate(row_labels):
        y = margin_t + cell_h * i
        parts.append(
            f'<text x="{margin_l - 8}" y="{y + cell_h / 2 + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(rl)}</text>'
        )
        for j in range(nc):
            val = data[i][j]
            x = margin_l + cell_w * j
            # 색 보간: 낮 -> 보라, 높 -> 초록
            ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0.5
            r = int(167 * (1 - ratio) + 0 * ratio)
            g = int(139 * (1 - ratio) + 224 * ratio)
            b = int(250 * (1 - ratio) + 158 * ratio)
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w:.1f}" height="{cell_h:.1f}" '
                f'fill="rgb({r},{g},{b})" opacity="0.25" stroke="{C_BORDER}" stroke-width="0.5"/>'
            )
            parts.append(
                f'<text x="{x + cell_w / 2:.1f}" y="{y + cell_h / 2 + 4:.1f}" '
                f'text-anchor="middle" font-size="10" fill="{C_TEXT_SEC}" '
                f'font-family="{FONT}">{_fmt(val)}{unit}</text>'
            )

    return _chart_wrap(title, "\n".join(parts), sec, w=int(w), h=int(h))


def svg_grouped_bar(
    title: str,
    labels: Sequence[str],
    group_names: Sequence[str],
    group_data: Sequence[Sequence[float]],
    sec: int = 0,
    unit: str = "",
) -> str:
    """그룹 막대 차트. group_data[group_idx][label_idx]."""
    n = len(labels)
    ng = len(group_names)
    if n == 0 or ng == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    all_vals = [v for gd in group_data for v in gd]
    v_min = min(0, min(all_vals))
    v_max = max(all_vals) * 1.15

    cluster_w = area_w / n
    bar_w = min(cluster_w / (ng + 1), 30)

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    for i, lbl in enumerate(labels):
        cx = margin_l + cluster_w * (i + 0.5)
        parts.append(
            f'<text x="{cx:.1f}" y="{VB_H - margin_b + 18:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(str(lbl))}</text>'
        )
        for g in range(ng):
            val = group_data[g][i]
            bx = cx - (ng * bar_w) / 2 + g * bar_w
            ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
            h = ratio * area_h
            y = VB_H - margin_b - h
            c = _pick_color(g)
            parts.append(
                f'<rect x="{bx:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
                f'height="{h:.1f}" rx="2" fill="{c}" opacity="0.85"/>'
            )

    # 범례
    for g, gn in enumerate(group_names):
        lx = margin_l + g * 100
        parts.append(
            f'<rect x="{lx}" y="{VB_H - 8}" width="10" height="3" rx="1" fill="{_pick_color(g)}"/>'
            f'<text x="{lx + 14}" y="{VB_H - 4}" font-size="10" fill="{C_TEXT_SEC}" '
            f'font-family="{FONT}">{_esc(gn)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_bubble_risk(
    title: str,
    risks: Sequence[tuple[str, float, float, float]],
    sec: int = 0,
) -> str:
    """버블 리스크 맵. risks = [(label, probability, impact, severity)]."""
    if not risks:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, 0, 10))

    parts.append(
        f'<text x="{VB_W / 2}" y="{VB_H - 4}" text-anchor="middle" '
        f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">발생 확률</text>'
    )
    parts.append(
        f'<text x="14" y="{VB_H / 2}" text-anchor="middle" '
        f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}" '
        f'transform="rotate(-90,14,{VB_H / 2})">영향도</text>'
    )

    max_sev = max(s for _, _, _, s in risks) or 1
    for i, (lbl, prob, impact, sev) in enumerate(risks):
        sx = margin_l + prob / 10 * area_w
        sy = VB_H - margin_b - impact / 10 * area_h
        r = max(8, min(sev / max_sev * 30, 35))
        c = C_RED if sev >= 7 else ("#FFB84D" if sev >= 4 else C_GREEN)
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r:.0f}" fill="{c}" opacity="0.4"/>')
        parts.append(
            f'<text x="{sx:.1f}" y="{sy + 4:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(lbl)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_per_band(
    title: str,
    years: Sequence[str],
    prices: Sequence[float],
    per_levels: Sequence[tuple[str, Sequence[float], str]],
    sec: int = 0,
) -> str:
    """PER 밴드 차트. per_levels = [(label, values_per_year, color), ...]."""
    n = len(years)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    all_vals = list(prices) + [v for _, vals, _ in per_levels for v in vals]
    v_min = min(all_vals) * 0.9
    v_max = max(all_vals) * 1.1

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    def to_xy(i: int, val: float) -> tuple[float, float]:
        x = margin_l + area_w * i / max(n - 1, 1)
        ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
        y = VB_H - margin_b - ratio * area_h
        return x, y

    # PER 밴드 라인
    for lbl, vals, color in per_levels:
        pts = " ".join(f"{to_xy(i, v)[0]:.1f},{to_xy(i, v)[1]:.1f}" for i, v in enumerate(vals))
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="1" stroke-dasharray="4,3" opacity="0.6"/>'
        )
        lx, ly = to_xy(n - 1, vals[-1])
        parts.append(
            f'<text x="{lx + 4:.1f}" y="{ly + 3:.1f}" font-size="9" '
            f'fill="{color}" font-family="{FONT}">{_esc(lbl)}</text>'
        )

    # 주가 라인
    pts = " ".join(f"{to_xy(i, p)[0]:.1f},{to_xy(i, p)[1]:.1f}" for i, p in enumerate(prices))
    parts.append(
        f'<polyline points="{pts}" fill="none" stroke="{C_PURPLE}" stroke-width="2.5"/>'
    )
    for i, p in enumerate(prices):
        x, y = to_xy(i, p)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{C_PURPLE}"/>')

    # X 라벨
    for i, yr in enumerate(years):
        x, _ = to_xy(i, 0)
        parts.append(
            f'<text x="{x:.1f}" y="{VB_H - margin_b + 18:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(yr)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_flow_diagram(
    title: str,
    stages: Sequence[tuple[str, str]],
    sec: int = 0,
) -> str:
    """플로우 다이어그램. stages = [(label, description), ...]."""
    n = len(stages)
    if n == 0:
        return ""

    box_w, box_h = 110, 50
    gap_x = 30
    total_w = n * box_w + (n - 1) * gap_x
    start_x = (VB_W - total_w) / 2
    cy = VB_H / 2

    parts: list[str] = []

    for i, (lbl, desc) in enumerate(stages):
        x = start_x + i * (box_w + gap_x)
        c = _pick_color(i)

        parts.append(
            f'<rect x="{x:.1f}" y="{cy - box_h / 2:.1f}" width="{box_w}" height="{box_h}" '
            f'rx="8" fill="{c}" opacity="0.15" stroke="{c}" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{x + box_w / 2:.1f}" y="{cy - 4:.1f}" text-anchor="middle" '
            f'font-size="11" fill="{C_TEXT_SEC}" font-family="{FONT}" font-weight="700">'
            f"{_esc(lbl)}</text>"
        )
        parts.append(
            f'<text x="{x + box_w / 2:.1f}" y="{cy + 12:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(desc)}</text>'
        )

        # 화살표
        if i < n - 1:
            ax = x + box_w + 2
            parts.append(
                f'<line x1="{ax:.1f}" y1="{cy}" x2="{ax + gap_x - 4:.1f}" y2="{cy}" '
                f'stroke="{C_TEXT_SEC}" stroke-width="1.5" marker-end="url(#arrow)"/>'
            )

    # 화살표 마커 정의
    parts.insert(
        0,
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" '
        f'fill="{C_TEXT_SEC}"/></marker></defs>',
    )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_area(
    title: str,
    labels: Sequence[str],
    datasets: Sequence[tuple[str, Sequence[float], str]],
    sec: int = 0,
    unit: str = "",
) -> str:
    """영역 차트. datasets = [(name, values, color), ...]."""
    n = len(labels)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 20, 50
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    all_vals = [v for _, vals, _ in datasets for v in vals]
    v_min = min(all_vals)
    v_max = max(all_vals)
    pad = (v_max - v_min) * 0.1 or 1
    v_min -= pad
    v_max += pad

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    y_base = VB_H - margin_b

    for name, vals, color in datasets:
        pts_top: list[str] = []
        for i, val in enumerate(vals):
            x = margin_l + area_w * i / max(n - 1, 1)
            ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
            y = y_base - ratio * area_h
            pts_top.append(f"{x:.1f},{y:.1f}")

        x_first = margin_l
        x_last = margin_l + area_w

        polygon_pts = f"{x_first:.1f},{y_base:.1f} " + " ".join(pts_top) + f" {x_last:.1f},{y_base:.1f}"
        parts.append(
            f'<polygon points="{polygon_pts}" fill="{color}" opacity="0.12"/>'
        )
        parts.append(
            f'<polyline points="{" ".join(pts_top)}" fill="none" '
            f'stroke="{color}" stroke-width="2"/>'
        )

    # X 라벨
    for i, lbl in enumerate(labels):
        x = margin_l + area_w * i / max(n - 1, 1)
        parts.append(
            f'<text x="{x:.1f}" y="{VB_H - margin_b + 18:.1f}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(str(lbl))}</text>'
        )

    # 범례
    for di, (name, _, color) in enumerate(datasets):
        lx = margin_l + di * 110
        parts.append(
            f'<rect x="{lx}" y="{VB_H - 8}" width="10" height="3" rx="1" fill="{color}"/>'
            f'<text x="{lx + 14}" y="{VB_H - 4}" font-size="10" fill="{C_TEXT_SEC}" '
            f'font-family="{FONT}">{_esc(name)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_timeline(
    title: str,
    events: Sequence[tuple[str, str, str]],
    sec: int = 0,
) -> str:
    """타임라인. events = [(date, label, color), ...]."""
    n = len(events)
    if n == 0:
        return ""

    margin_l, margin_r = 40, 40
    area_w = VB_W - margin_l - margin_r
    cy = VB_H / 2

    parts: list[str] = []

    # 중앙 라인
    parts.append(
        f'<line x1="{margin_l}" y1="{cy}" x2="{VB_W - margin_r}" y2="{cy}" '
        f'stroke="{C_BORDER}" stroke-width="2"/>'
    )

    for i, (date, lbl, color) in enumerate(events):
        x = margin_l + area_w * i / max(n - 1, 1)
        above = i % 2 == 0

        # 노드
        parts.append(f'<circle cx="{x:.1f}" cy="{cy}" r="5" fill="{color}"/>')

        # 수직 라인
        y_end = cy - 50 if above else cy + 50
        parts.append(
            f'<line x1="{x:.1f}" y1="{cy}" x2="{x:.1f}" y2="{y_end}" '
            f'stroke="{color}" stroke-width="1" opacity="0.5"/>'
        )

        # 텍스트
        ty_date = y_end - 14 if above else y_end + 10
        ty_lbl = y_end - 2 if above else y_end + 22
        parts.append(
            f'<text x="{x:.1f}" y="{ty_date}" text-anchor="middle" '
            f'font-size="9" fill="{color}" font-family="{FONT}" font-weight="700">'
            f"{_esc(date)}</text>"
        )
        parts.append(
            f'<text x="{x:.1f}" y="{ty_lbl}" text-anchor="middle" '
            f'font-size="10" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(lbl)}</text>'
        )

    return _chart_wrap(title, "\n".join(parts), sec)


def svg_annotated_price(
    title: str,
    dates: Sequence[str],
    prices: Sequence[float],
    events: Sequence[tuple[int, str, str]] | None = None,
    sec: int = 0,
) -> str:
    """주석 달린 주가 차트. events = [(index, label, color), ...]."""
    n = len(dates)
    if n == 0:
        return ""

    margin_l, margin_r, margin_t, margin_b = 70, 30, 30, 50
    area_w = VB_W - margin_l - margin_r
    area_h = VB_H - margin_t - margin_b

    v_min = min(prices) * 0.95
    v_max = max(prices) * 1.05

    parts: list[str] = []
    parts.append(_grid_lines(margin_l, VB_W - margin_r, VB_H - margin_b, margin_t, v_min, v_max))

    def to_xy(i: int, val: float) -> tuple[float, float]:
        x = margin_l + area_w * i / max(n - 1, 1)
        ratio = (val - v_min) / (v_max - v_min) if v_max != v_min else 0
        y = VB_H - margin_b - ratio * area_h
        return x, y

    # 영역
    pts_top = [f"{to_xy(i, p)[0]:.1f},{to_xy(i, p)[1]:.1f}" for i, p in enumerate(prices)]
    x_first = margin_l
    x_last = margin_l + area_w
    y_base = VB_H - margin_b
    polygon = f"{x_first:.1f},{y_base:.1f} " + " ".join(pts_top) + f" {x_last:.1f},{y_base:.1f}"
    parts.append(f'<polygon points="{polygon}" fill="{C_PURPLE}" opacity="0.08"/>')
    parts.append(
        f'<polyline points="{" ".join(pts_top)}" fill="none" '
        f'stroke="{C_PURPLE}" stroke-width="2"/>'
    )

    # X 라벨 (간격 조절)
    step = max(1, n // 8)
    for i in range(0, n, step):
        x, _ = to_xy(i, 0)
        parts.append(
            f'<text x="{x:.1f}" y="{VB_H - margin_b + 18:.1f}" text-anchor="middle" '
            f'font-size="9" fill="{C_TEXT_SEC}" font-family="{FONT}">{_esc(dates[i])}</text>'
        )

    # 이벤트 주석
    if events:
        for idx, lbl, color in events:
            if 0 <= idx < n:
                ex, ey = to_xy(idx, prices[idx])
                parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{color}"/>')
                parts.append(
                    f'<line x1="{ex:.1f}" y1="{ey - 5:.1f}" x2="{ex:.1f}" y2="{ey - 30:.1f}" '
                    f'stroke="{color}" stroke-width="1"/>'
                )
                parts.append(
                    f'<text x="{ex:.1f}" y="{ey - 34:.1f}" text-anchor="middle" '
                    f'font-size="9" fill="{color}" font-family="{FONT}">{_esc(lbl)}</text>'
                )

    return _chart_wrap(title, "\n".join(parts), sec)


# ============================================================
#  테이블
# ============================================================

def table(
    headers: Sequence[str],
    rows: Sequence[Sequence],
    highlight_rows: Sequence[int] | None = None,
    sec: int = 0,
    title: str = "",
    src: str = "",
) -> str:
    """HD건설기계 패턴 테이블. class='data' 필수.
    highlight_rows: 0-based 인덱스 리스트 -> class='highlight-row' 추가.
    음수값: 빨간 괄호 표기.
    """
    hr_set = set(highlight_rows or [])
    fn = fig_num(sec) if sec and title else ""
    caption = f"{fn} {_esc(title)}" if fn else _esc(title)

    out: list[str] = []
    if title:
        out.append(f'<div class="chart-title" style="margin-bottom:4px">{caption}</div>')

    out.append('<table class="data">')
    out.append("<thead><tr>")
    for h in headers:
        out.append(f"<th>{_esc(str(h))}</th>")
    out.append("</tr></thead>")

    out.append("<tbody>")
    for ri, row in enumerate(rows):
        cls = ' class="highlight-row"' if ri in hr_set else ""
        out.append(f"<tr{cls}>")
        for ci, cell in enumerate(row):
            if isinstance(cell, (int, float)) and cell < 0:
                val_html = f'<span style="color:var(--red)">({_fmt(abs(cell))})</span>'
            elif isinstance(cell, (int, float)):
                val_html = _fmt(cell)
            else:
                val_html = _esc(str(cell))
            out.append(f"<td>{val_html}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")

    if src:
        out.append(f'<div class="chart-source">출처: {_esc(src)}</div>')

    return "\n".join(out)


# ============================================================
#  레이아웃 함수
# ============================================================

def section_header(num: int, title: str, stock_name: str = "", stock_code: str = "") -> str:
    """섹션 헤더. HD건설기계 클래스명."""
    sub = ""
    if stock_name and stock_code:
        sub = (
            f'<div class="section-subheader">'
            f"Equity Research Report | {_esc(stock_name)} ({_esc(stock_code)})</div>"
        )
    return (
        f"{sub}"
        f'<div class="section-header">'
        f'<div class="section-num">{num}</div>'
        f'<div class="section-title">{_esc(title)}</div>'
        f"</div>"
    )


def sidebar_wrap(kv_pairs: Sequence[tuple[str, str]], content_html: str) -> str:
    """사이드바 레이아웃. sidebar-layout > sidebar-kw + content-area."""
    kw_html = ""
    for key, val in kv_pairs:
        kw_html += f'<div class="kw">{_esc(key)}</div><div class="kw-val">{_esc(val)}</div>'

    return (
        f'<div class="sidebar-layout">'
        f'<div class="sidebar-kw">{kw_html}</div>'
        f'<div class="content-area">{content_html}</div>'
        f"</div>"
    )


# ============================================================
#  고급 컴포넌트
# ============================================================

def counter_arg(concern: str, rebuttal: str) -> str:
    """반론 논파 컴포넌트."""
    return (
        f'<div class="counter-arg">'
        f'<div class="counter-concern">{_esc(concern)}</div>'
        f'<div class="counter-rebuttal">{_esc(rebuttal)}</div>'
        f"</div>"
    )


def callout(text: str) -> str:
    """KEY TAKEAWAY 콜아웃."""
    return f'<div class="callout">{_esc(text)}</div>'


def expand_card(title: str, meta: str, content: str) -> str:
    """접기/펼치기 카드 (<details> 기반)."""
    return (
        f'<details class="expand-card">'
        f"<summary>{_esc(title)}"
        f'<span class="expand-meta">{_esc(meta)}</span></summary>'
        f'<div class="expand-content">{content}</div>'
        f"</details>"
    )


def add_source(chart_html: str, src_text: str) -> str:
    """차트 HTML에 출처 텍스트 추가."""
    return f'{chart_html}\n<div class="chart-source">출처: {_esc(src_text)}</div>'


# ============================================================
#  HD건설기계 고유 컴포넌트
# ============================================================

def metric_grid(items: Sequence[tuple[str, str, str, str]]) -> str:
    """메트릭 그리드. items = [(label, value, sub, direction)].
    direction: 'up' | 'down' | '' -> mc-up / mc-down.
    """
    cards: list[str] = []
    for label, value, sub, direction in items:
        dir_cls = "mc-up" if direction == "up" else ("mc-down" if direction == "down" else "")
        sub_html = f'<div class="mc-sub {dir_cls}">{_esc(sub)}</div>' if sub else ""
        cards.append(
            f'<div class="metric-card">'
            f'<div class="mc-label">{_esc(label)}</div>'
            f'<div class="mc-value">{_esc(value)}</div>'
            f"{sub_html}</div>"
        )
    return f'<div class="metric-grid">{"".join(cards)}</div>'


def scenario_grid(
    bull: dict[str, str],
    base: dict[str, str],
    bear: dict[str, str],
) -> str:
    """시나리오 그리드. 각 dict: {price, upside, prob, desc}."""
    def _card(data: dict[str, str], variant: str, label: str) -> str:
        return (
            f'<div class="scenario-card {variant}">'
            f'<div class="sc-label">{label}</div>'
            f'<div class="sc-price">{_esc(data.get("price", ""))}</div>'
            f'<div class="sc-upside">{_esc(data.get("upside", ""))}</div>'
            f'<div class="sc-prob">{_esc(data.get("prob", ""))}</div>'
            f'<div class="sc-desc">{_esc(data.get("desc", ""))}</div>'
            f"</div>"
        )

    return (
        f'<div class="scenario-grid">'
        f'{_card(bull, "bull", "BULL")}'
        f'{_card(base, "base", "BASE")}'
        f'{_card(bear, "bear", "BEAR")}'
        f"</div>"
    )


def risk_grid(risks: Sequence[tuple[str, str, str]]) -> str:
    """리스크 그리드. risks = [(title, prob_level, impact_text)].
    prob_level: 'high' | 'med' | 'low'.
    """
    level_label = {"high": "높음", "med": "중간", "low": "낮음"}
    cards: list[str] = []
    for r_title, prob, impact in risks:
        cls = f"risk-{prob}" if prob in ("high", "med", "low") else "risk-med"
        cards.append(
            f'<div class="risk-card">'
            f'<div class="risk-title">{_esc(r_title)}</div>'
            f'<span class="risk-prob {cls}">{level_label.get(prob, prob)}</span>'
            f'<div class="risk-impact">{_esc(impact)}</div>'
            f"</div>"
        )
    return f'<div class="risk-grid">{"".join(cards)}</div>'


def chart_with_insight(chart_html: str, insight: str, src: str = "") -> str:
    """차트 + 해석 블록. SMIC 패턴: 차트 아래 2-3줄 해석문."""
    src_html = f'<div class="chart-source">출처: {_esc(src)}</div>' if src else ""
    return (
        f'<div class="chart-box">{chart_html}{src_html}'
        f'<div class="chart-insight">{_esc(insight)}</div></div>'
    )

def chart_pair(chart1: str, chart2: str) -> str:
    """두 차트를 2열로 배치. HD건설기계 .chart-pair 패턴."""
    return (
        f'<div class="chart-pair">'
        f'<div class="chart-box">{chart1}</div>'
        f'<div class="chart-box">{chart2}</div>'
        f'</div>'
    )

def kill_condition_gauge(conditions: list[tuple[str, str, str, str]]) -> str:
    """Kill Condition 시각화. conditions = [(조건, 현재, 여유, 상태)].
    상태: 'safe'=초록, 'warn'=노랑, 'danger'=빨강"""
    cards = []
    for cond, current, margin, status in conditions:
        color = {"safe": "var(--green)", "warn": "#FFB84D", "danger": "var(--red)"}.get(status, "var(--text-sec)")
        cards.append(
            f'<div class="kill-card">'
            f'<div class="kill-status" style="color:{color}">●</div>'
            f'<div class="kill-cond">{_esc(cond)}</div>'
            f'<div class="kill-current">현재: {_esc(current)}</div>'
            f'<div class="kill-margin">여유: {_esc(margin)}</div>'
            f'</div>'
        )
    return f'<div class="kill-grid">{"".join(cards)}</div>'

def assumption_tracker(assumptions: list[tuple[str, str, str, str, str]]) -> str:
    """가정 추적기. assumptions = [(가정, 수치, 출처, 반증조건, 모니터링주기)]."""
    return table(
        ["가정", "수치", "출처", "반증 조건", "모니터링"],
        [[a[0], a[1], a[2], a[3], a[4]] for a in assumptions],
        title="Assumption Tracker — 모든 가정과 반증 조건",
    )
