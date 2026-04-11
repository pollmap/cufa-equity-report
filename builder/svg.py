"""CUFA Builder — SVG 차트 헬퍼 (32종).

순수 Python으로 SVG 문자열을 생성. matplotlib 의존 0.
모든 함수는 `<div class="chart-box">...</div>` 로 래핑된 HTML 문자열 반환.

v13 금지: svg_radar 삭제. 레이더 차트가 필요한 경우
`svg_grouped_bar()` 또는 `svg_scatter()` 로 대체.

카테고리:
- Core (1st tier): donut, bar, line, hbar, waterfall, scatter, football,
  heatmap, grouped_bar, bubble_risk, flow_diagram
- Extended (2nd tier): area, timeline, roe_pbr_path, rebased_price,
  candlestick, boxplot, bullet, gantt, pareto, bump, sparkline, lollipop,
  histogram, slope, tornado, treemap
- Advanced (3rd tier): sankey, waffle, gauge, marimekko, pictogram
"""
from __future__ import annotations

import math
from typing import Sequence

from .figure import fig_num


# ═══════════════════════════════════════════════════════════════════════
# TIER 1 — CORE CHARTS (11종)
# ═══════════════════════════════════════════════════════════════════════

def svg_donut(title, segments, cx=180, cy=150, r=100, ir=55, width=360, height=300, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    total = sum(v for _, v, _ in segments)
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    angle = -90
    for label, val, color in segments:
        pct = val / total
        a1 = math.radians(angle); a2 = math.radians(angle + pct * 360)
        x1o, y1o = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2o, y2o = cx + r * math.cos(a2), cy + r * math.sin(a2)
        x1i, y1i = cx + ir * math.cos(a2), cy + ir * math.sin(a2)
        x2i, y2i = cx + ir * math.cos(a1), cy + ir * math.sin(a1)
        large = 1 if pct > 0.5 else 0
        svg += f'<path d="M{x1o:.1f},{y1o:.1f} A{r},{r} 0 {large},1 {x2o:.1f},{y2o:.1f} L{x1i:.1f},{y1i:.1f} A{ir},{ir} 0 {large},0 {x2i:.1f},{y2i:.1f} Z" fill="{color}" opacity="0.85"/>\n'
        mid_a = math.radians(angle + pct * 180)
        tx = cx + (r + 18) * math.cos(mid_a); ty = cy + (r + 18) * math.sin(mid_a)
        if pct >= 0.05:
            svg += f'<text x="{tx:.0f}" y="{ty:.0f}" fill="var(--text)" font-size="11" text-anchor="middle">{pct*100:.0f}%</text>\n'
        angle += pct * 360
    svg += f'<text x="{cx}" y="{cy-4}" fill="var(--purple-light)" font-size="14" font-weight="700" text-anchor="middle">{total:,.0f}</text>\n'
    ly = height - 10 - len(segments) * 16
    for i, (label, val, color) in enumerate(segments):
        lx = width - 160
        svg += f'<rect x="{lx}" y="{ly + i*16}" width="10" height="10" rx="2" fill="{color}"/>\n'
        svg += f'<text x="{lx+14}" y="{ly + i*16 + 9}" fill="var(--text-sec)" font-size="11">{label} ({val:,.0f})</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_bar(title, labels, values, colors=None, width=600, height=260, show_line=False, line_values=None, line_label="", y_suffix="", sec=0, unit="", auto_base=True):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if colors is None: colors = ["#7C6AF7"] * len(labels)
    elif isinstance(colors, str): colors = [colors] * len(labels)
    max_val = max(abs(v) for v in values) if values else 1
    if auto_base and all(v > 0 for v in values) and min(values) / max(values) > 0.3:
        y_base = min(values) * 0.7
    else:
        y_base = 0
    max_display = max(abs(v) - y_base for v in values) if values else 1
    bar_area_h = height - 70; bar_w = min(40, (width - 80) / len(labels) * 0.55); gap = (width - 60) / len(labels)
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    if unit: svg += f'<text x="42" y="14" fill="var(--text-sec)" font-size="11">(단위: {unit})</text>\n'
    baseline_y = height - 40
    svg += f'<line x1="40" y1="{baseline_y}" x2="{width-20}" y2="{baseline_y}" stroke="var(--border)" stroke-width="1"/>\n'
    for g in range(1, 5):
        gy = baseline_y - (g / 4) * bar_area_h * 0.85; gval = y_base + max_display * g / 4
        svg += f'<line x1="40" y1="{gy:.1f}" x2="{width-20}" y2="{gy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3"/>\n'
        svg += f'<text x="36" y="{gy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{gval:,.0f}</text>\n'
    x_font = 9 if any(len(str(l)) > 5 for l in labels) else 11
    for i, (lbl, val) in enumerate(zip(labels, values)):
        x = 50 + i * gap; bh = ((abs(val) - y_base) / max_display) * bar_area_h * 0.85; y = baseline_y - bh
        svg += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="3" fill="{colors[i]}" opacity="0.8"/>\n'
        svg += f'<text x="{x + bar_w/2:.1f}" y="{y - 8:.1f}" fill="var(--text)" font-size="11" text-anchor="middle">{val:,.0f}{y_suffix}</text>\n'
        svg += f'<text x="{x + bar_w/2:.1f}" y="{baseline_y + 14:.1f}" fill="var(--text-sec)" font-size="{x_font}" text-anchor="middle">{lbl}</text>\n'
    if show_line and line_values:
        max_lv = max(abs(v) for v in line_values) if line_values else 1
        points = []
        for i, lv in enumerate(line_values):
            x = 50 + i * gap + bar_w / 2; y = baseline_y - (lv / max_lv) * bar_area_h * 0.85
            points.append(f"{x:.1f},{y:.1f}")
        svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="var(--negative)" stroke-width="2" stroke-linecap="round"/>\n'
        for i, (pt, lv) in enumerate(zip(points, line_values)):
            x, y = pt.split(",")
            svg += f'<circle cx="{x}" cy="{y}" r="3" fill="var(--negative)"/>\n'
            svg += f'<text x="{x}" y="{float(y)-8:.1f}" fill="var(--negative)" font-size="11" text-anchor="middle">{lv:.1f}%</text>\n'
        svg += f'<text x="{width - 20}" y="20" fill="var(--negative)" font-size="11" text-anchor="end">{line_label} (우)</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_line(title, labels, datasets, width=600, height=260, sec=0, unit=""):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    all_vals = [v for _, vals, _ in datasets for v in vals]
    min_v, max_v = min(all_vals), max(all_vals); rng = max_v - min_v if max_v != min_v else 1
    area_h = height - 70; gap = (width - 80) / max(len(labels) - 1, 1)
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    if unit: svg += f'<text x="42" y="14" fill="var(--text-sec)" font-size="11">(단위: {unit})</text>\n'
    baseline_y = height - 40
    for g in range(1, 5):
        gy = baseline_y - (g / 4) * area_h * 0.85; gval = min_v + rng * g / 4
        svg += f'<line x1="40" y1="{gy:.1f}" x2="{width-20}" y2="{gy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3"/>\n'
        svg += f'<text x="36" y="{gy+4:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="end">{gval:,.1f}</text>\n'
    for i, lbl in enumerate(labels):
        x = 50 + i * gap
        svg += f'<text x="{x:.1f}" y="{baseline_y + 14:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{lbl}</text>\n'
    for name, vals, color in datasets:
        points = []
        for i, v in enumerate(vals):
            x = 50 + i * gap; y = baseline_y - ((v - min_v) / rng) * area_h * 0.85
            points.append(f"{x:.1f},{y:.1f}")
        svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>\n'
        for i, (pt, v) in enumerate(zip(points, vals)):
            x, y = pt.split(",")
            svg += f'<circle cx="{x}" cy="{y}" r="3" fill="{color}"/>\n'
            if i == 0 or i == len(vals)-1 or v == max(vals) or v == min(vals):
                svg += f'<text x="{x}" y="{float(y)-10:.1f}" fill="{color}" font-size="10" text-anchor="middle">{v:,.0f}</text>\n'
    lx = 60
    for i, (name, _, color) in enumerate(datasets):
        svg += f'<line x1="{lx}" y1="12" x2="{lx+16}" y2="12" stroke="{color}" stroke-width="2"/>\n'
        svg += f'<text x="{lx+20}" y="15" fill="{color}" font-size="11">{name}</text>\n'
        lx += len(name) * 8 + 40
    svg += '</svg></div>\n'
    return svg


def svg_hbar(title, labels, values, colors=None, width=700, height=None, val_suffix="", sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if height is None: height = 40 + len(labels) * 32
    if colors is None: colors = ["#7C6AF7"] * len(labels)
    elif isinstance(colors, str): colors = [colors] * len(labels)
    max_val = max(abs(v) for v in values) if values else 1
    bar_area_w = width - 200
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (lbl, val) in enumerate(zip(labels, values)):
        y = 20 + i * 30; bw = (abs(val) / max_val) * bar_area_w * 0.85
        svg += f'<text x="118" y="{y + 14}" fill="var(--text-sec)" font-size="11" text-anchor="end">{lbl}</text>\n'
        svg += f'<rect x="124" y="{y + 2}" width="{bw:.1f}" height="18" rx="3" fill="{colors[i % len(colors)]}" opacity="0.8"/>\n'
        svg += f'<text x="{130 + bw:.1f}" y="{y + 14}" fill="var(--text)" font-size="11">{val:,.1f}{val_suffix}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_waterfall(title, items, width=600, height=350, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    max_cum = 0; cum = 0; cum_vals = []
    for label, val, typ in items:
        if typ == 'total': cum_vals.append((cum, cum))
        else: start = cum; cum += val if typ == 'up' else -val; cum_vals.append((start, cum))
        max_cum = max(max_cum, abs(cum), abs(cum_vals[-1][0]), abs(cum_vals[-1][1]))
    area_h = height - 80; gap = (width - 80) / len(items); bar_w = gap * 0.55
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    baseline_y = height - 45; scale = area_h * 0.75 / max_cum if max_cum else 1
    for i, ((s, e), (label, val, typ)) in enumerate(zip(cum_vals, items)):
        x = 50 + i * gap
        if typ == 'total': y_top = baseline_y - e * scale; bh = e * scale; color = "var(--purple)"
        elif typ == 'up': y_top = baseline_y - max(s, e) * scale; bh = abs(val) * scale; color = "var(--positive)"
        else: y_top = baseline_y - max(s, e) * scale; bh = abs(val) * scale; color = "var(--negative)"
        svg += f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w:.1f}" height="{max(bh, 2):.1f}" rx="2" fill="{color}" opacity="0.8"/>\n'
        svg += f'<text x="{x + bar_w/2:.1f}" y="{y_top - 6:.1f}" fill="var(--text)" font-size="11" text-anchor="middle">{val:,}</text>\n'
        svg += f'<text x="{x + bar_w/2:.1f}" y="{baseline_y + 14:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{label}</text>\n'
        if i < len(items) - 1:
            svg += f'<line x1="{x + bar_w:.1f}" y1="{baseline_y - e * scale:.1f}" x2="{50 + (i+1)*gap:.1f}" y2="{baseline_y - e * scale:.1f}" stroke="var(--border)" stroke-width="1" stroke-dasharray="3"/>\n'
    svg += '</svg></div>\n'
    return svg


def svg_scatter(title, points, x_label, y_label, width=500, height=350, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    all_x = [p[1] for p in points]; all_y = [p[2] for p in points]
    min_x, max_x = min(all_x)*0.8, max(all_x)*1.2; min_y, max_y = min(all_y)*0.8, max(all_y)*1.2
    rng_x = max_x - min_x if max_x != min_x else 1; rng_y = max_y - min_y if max_y != min_y else 1
    area_x, area_y = width - 100, height - 80
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<text x="{width/2}" y="{height-10}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{x_label}</text>\n'
    svg += f'<text x="15" y="{height/2}" fill="var(--text-sec)" font-size="11" text-anchor="middle" transform="rotate(-90,15,{height/2})">{y_label}</text>\n'
    for name, x, y, color, size in points:
        px = 60 + ((x - min_x) / rng_x) * area_x; py = (height - 50) - ((y - min_y) / rng_y) * area_y + 20
        svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{size}" fill="{color}" opacity="0.7"/>\n'
        svg += f'<text x="{px:.1f}" y="{py - size - 4:.1f}" fill="var(--text)" font-size="11" text-anchor="middle">{name}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_football(title, rows, current, width=600, height=None, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if height is None: height = 50 + len(rows) * 50
    all_vals = [v for _, lo, hi, _ in rows for v in (lo, hi)] + [current]
    min_v, max_v = min(all_vals) * 0.9, max(all_vals) * 1.1; rng = max_v - min_v if max_v != min_v else 1
    bar_area = width - 220
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    cx = 160 + ((current - min_v) / rng) * bar_area
    svg += f'<line x1="{cx:.1f}" y1="10" x2="{cx:.1f}" y2="{height-10}" stroke="var(--negative)" stroke-width="1.5" stroke-dasharray="5"/>\n'
    svg += f'<text x="{cx:.1f}" y="10" fill="var(--text)" font-size="11" text-anchor="middle">현재 {current:,}</text>\n'
    for i, (method, lo, hi, color) in enumerate(rows):
        y = 30 + i * 45; x1 = 160 + ((lo - min_v) / rng) * bar_area; x2 = 160 + ((hi - min_v) / rng) * bar_area
        svg += f'<text x="148" y="{y + 14}" fill="var(--text-sec)" font-size="11" text-anchor="end">{method}</text>\n'
        svg += f'<rect x="{x1:.1f}" y="{y}" width="{x2-x1:.1f}" height="22" rx="4" fill="{color}" opacity="0.6"/>\n'
        svg += f'<text x="{x1 - 4:.1f}" y="{y + 14}" fill="{color}" font-size="11" text-anchor="end">{lo:,}</text>\n'
        svg += f'<text x="{x2 + 4:.1f}" y="{y + 14}" fill="{color}" font-size="11">{hi:,}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_heatmap(title, row_labels, col_labels, data, width=550, height=None, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if height is None: height = 60 + len(row_labels) * 36
    all_v = [v for row in data for v in row]; min_v, max_v = min(all_v), max(all_v); rng = max_v - min_v if max_v != min_v else 1
    cell_w = min(70, (width - 120) / len(col_labels)); cell_h = 30
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for j, cl in enumerate(col_labels):
        x = 110 + j * cell_w
        svg += f'<text x="{x + cell_w/2:.1f}" y="20" fill="var(--text-sec)" font-size="11" text-anchor="middle">{cl}</text>\n'
    for i, (rl, row) in enumerate(zip(row_labels, data)):
        y = 30 + i * cell_h
        svg += f'<text x="105" y="{y + cell_h/2 + 4:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="end">{rl}</text>\n'
        for j, val in enumerate(row):
            x = 110 + j * cell_w; t = (val - min_v) / rng
            if t < 0.5: r_, g_, b_ = int(255 - t*2*130), int(77 + t*2*100), int(77 + t*2*100)
            else: r_, g_, b_ = int(125 - (t-0.5)*2*125), int(177 + (t-0.5)*2*47), int(177 - (t-0.5)*2*19)
            color = f"#{r_:02x}{g_:02x}{b_:02x}"
            svg += f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" rx="3" fill="{color}" opacity="0.7"/>\n'
            svg += f'<text x="{x + cell_w/2 - 1:.1f}" y="{y + cell_h/2 + 3:.1f}" fill="var(--text)" font-size="11" text-anchor="middle" font-weight="500">{val:,.0f}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_grouped_bar(title, labels, group_names, group_data, group_colors, width=600, height=260, y_suffix="", sec=0, unit=""):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    max_val = max(v for gd in group_data for v in gd); area_h = height - 70; n_groups = len(group_names)
    gap = (width - 80) / len(labels); bar_w = gap * 0.7 / n_groups
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    if unit: svg += f'<text x="42" y="14" fill="var(--text-sec)" font-size="11">(단위: {unit})</text>\n'
    baseline_y = height - 40
    for i, lbl in enumerate(labels):
        x_start = 50 + i * gap
        svg += f'<text x="{x_start + gap*0.35:.1f}" y="{baseline_y + 14:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{lbl}</text>\n'
        for g, (gd, gc) in enumerate(zip(group_data, group_colors)):
            x = x_start + g * bar_w; bh = (gd[i] / max_val) * area_h * 0.85; y = baseline_y - bh
            svg += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="2" fill="{gc}" opacity="0.8"/>\n'
    svg += '</svg></div>\n'
    return svg


def svg_bubble_risk(title, risks, width=650, height=450, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    area_x, area_y = width - 120, height - 100; ox, oy = 80, 30
    svg += f'<text x="{ox + area_x/2}" y="{oy + area_y + 35}" fill="var(--text-sec)" font-size="11" text-anchor="middle">발생 확률</text>\n'
    svg += f'<text x="15" y="{oy + area_y/2}" fill="var(--text-sec)" font-size="11" text-anchor="middle" transform="rotate(-90,15,{oy + area_y/2})">영향도</text>\n'
    for name, prob, impact, color, sz in risks:
        px = ox + (prob / 5) * area_x; py = oy + area_y - (impact / 5) * area_y
        svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{sz}" fill="{color}" opacity="0.5"/>\n'
        svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{sz}" fill="none" stroke="{color}" stroke-width="1.5"/>\n'
        svg += f'<text x="{px:.1f}" y="{py + 4:.1f}" fill="var(--text)" font-size="11" text-anchor="middle" font-weight="600">{name}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_flow_diagram(title, stages, width=700, height=180, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    n = len(stages); box_w = (width - 60) / n - 20
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (label, sublabel, color) in enumerate(stages):
        x = 30 + i * ((width - 60) / n); y = 30; bh = 80
        svg += f'<rect x="{x}" y="{y}" width="{box_w}" height="{bh}" rx="4" fill="{color}" opacity="0.15"/>\n'
        svg += f'<rect x="{x}" y="{y}" width="{box_w}" height="{bh}" rx="4" fill="none" stroke="{color}" stroke-width="1.5"/>\n'
        svg += f'<text x="{x+box_w/2}" y="{y+30}" fill="var(--text)" font-size="12" font-weight="700" text-anchor="middle">{label}</text>\n'
        svg += f'<text x="{x+box_w/2}" y="{y+52}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{sublabel}</text>\n'
        if i < n - 1:
            svg += f'<text x="{x + box_w + 12}" y="{y+40}" fill="var(--purple)" font-size="18" font-weight="700">\u2192</text>\n'
    svg += '</svg></div>\n'
    return svg


# ═══════════════════════════════════════════════════════════════════════
# TIER 2 — EXTENDED (16종)
# ═══════════════════════════════════════════════════════════════════════

def svg_area(title, labels, datasets, width=700, height=300, sec=0, unit=""):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    n_points = len(labels); cumulative = [[0]*n_points]
    for _, vals, _ in datasets:
        prev = cumulative[-1]; cumulative.append([prev[i] + vals[i] for i in range(n_points)])
    max_val = max(cumulative[-1]) if cumulative[-1] else 1
    area_h = height - 70; gap = (width - 80) / max(n_points - 1, 1); baseline_y = height - 40
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    if unit: svg += f'<text x="42" y="14" fill="var(--text-sec)" font-size="11">(단위: {unit})</text>\n'
    for idx in range(len(datasets)-1, -1, -1):
        name, vals, color = datasets[idx]; top = cumulative[idx+1]; bot = cumulative[idx]
        path = f'M{50},{baseline_y} '
        for i in range(n_points):
            x = 50 + i * gap; y = baseline_y - (top[i] / max_val) * area_h * 0.85; path += f'L{x:.1f},{y:.1f} '
        for i in range(n_points-1, -1, -1):
            x = 50 + i * gap; y = baseline_y - (bot[i] / max_val) * area_h * 0.85; path += f'L{x:.1f},{y:.1f} '
        path += 'Z'; svg += f'<path d="{path}" fill="{color}" opacity="0.6"/>\n'
    for i, lbl in enumerate(labels):
        x = 50 + i * gap; svg += f'<text x="{x:.1f}" y="{baseline_y+14:.1f}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{lbl}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_timeline(title, events, width=700, height=160, sec=0):
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    n = len(events)
    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    line_y = 60; gap = (width - 100) / max(n - 1, 1)
    svg += f'<line x1="40" y1="{line_y}" x2="{width-40}" y2="{line_y}" stroke="var(--border)" stroke-width="2"/>\n'
    for i, (date, desc, color) in enumerate(events):
        x = 50 + i * gap
        svg += f'<circle cx="{x:.1f}" cy="{line_y}" r="6" fill="{color}" stroke="var(--bg)" stroke-width="2"/>\n'
        svg += f'<text x="{x:.1f}" y="{line_y - 16}" fill="{color}" font-size="11" font-weight="700" text-anchor="middle">{date}</text>\n'
        dy = line_y + 22 + (i % 2) * 28
        svg += f'<text x="{x:.1f}" y="{dy}" fill="var(--text-sec)" font-size="11" text-anchor="middle">{desc}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_roe_pbr_path(title, paths, width=500, height=400, sec=0):
    """ROE-PBR 경로분석 차트. 분기별 ROE-PBR 좌표를 점+화살표로 연결."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    all_roe = [r for p in paths for r, _ in p['points']]
    all_pbr = [b for p in paths for _, b in p['points']]
    if not all_roe:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    roe_min, roe_max = min(all_roe), max(all_roe)
    pbr_min, pbr_max = min(all_pbr), max(all_pbr)
    roe_pad = max((roe_max - roe_min) * 0.15, 0.5)
    pbr_pad = max((pbr_max - pbr_min) * 0.15, 0.05)
    roe_lo, roe_hi = roe_min - roe_pad, roe_max + roe_pad
    pbr_lo, pbr_hi = pbr_min - pbr_pad, pbr_max + pbr_pad
    ml, mr, mt, mb = 60, 80, 45, 40
    cw, ch = width - ml - mr, height - mt - mb

    def sx(r): return ml + (r - roe_lo) / (roe_hi - roe_lo) * cw
    def sy(b): return mt + (1 - (b - pbr_lo) / (pbr_hi - pbr_lo)) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '<defs>\n'
    for i, p in enumerate(paths):
        c = p.get('color', '#7c6af7')
        svg += f'<marker id="arrow{i}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">'
        svg += f'<path d="M0,0 L8,3 L0,6 Z" fill="{c}"/></marker>\n'
    svg += '</defs>\n'
    svg += f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    svg += f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    y_ticks = 5
    for i in range(y_ticks + 1):
        v = pbr_lo + (pbr_hi - pbr_lo) * i / y_ticks
        yy = sy(v)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{v:.2f}</text>\n'
    x_ticks = 5
    for i in range(x_ticks + 1):
        v = roe_lo + (roe_hi - roe_lo) * i / x_ticks
        xx = sx(v)
        svg += f'<line x1="{xx:.1f}" y1="{mt}" x2="{xx:.1f}" y2="{mt+ch}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{xx:.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{v:.1f}</text>\n'
    svg += f'<text x="{ml+cw/2:.1f}" y="{height-4}" fill="var(--text)" font-size="11" text-anchor="middle">ROE (%)</text>\n'
    svg += f'<text x="14" y="{mt+ch/2:.1f}" fill="var(--text)" font-size="11" text-anchor="middle" transform="rotate(-90,14,{mt+ch/2:.1f})">PBR (배)</text>\n'
    for i, p in enumerate(paths):
        c = p.get('color', '#7c6af7')
        pts = p['points']
        if len(pts) < 2:
            if pts:
                px, py = sx(pts[0][0]), sy(pts[0][1])
                svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{c}"/>\n'
            continue
        for j in range(len(pts) - 1):
            x1, y1 = sx(pts[j][0]), sy(pts[j][1])
            x2, y2 = sx(pts[j+1][0]), sy(pts[j+1][1])
            svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="1.8" marker-end="url(#arrow{i})"/>\n'
        for j, (r, b) in enumerate(pts):
            px, py = sx(r), sy(b)
            svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{c}" stroke="var(--bg)" stroke-width="1.5"/>\n'
        fx, fy = sx(pts[0][0]), sy(pts[0][1])
        svg += f'<text x="{fx+8:.1f}" y="{fy-8:.1f}" fill="{c}" font-size="9" font-weight="600">시작</text>\n'
    if paths:
        last_p = paths[-1]
        if last_p['points']:
            lr, lb = last_p['points'][-1]
            lx, ly = sx(lr), sy(lb)
            lc = last_p.get('color', '#4ecdc4')
            svg += f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="6" fill="{lc}" stroke="var(--bg)" stroke-width="2"/>\n'
            svg += f'<text x="{lx+10:.1f}" y="{ly+4:.1f}" fill="{lc}" font-size="11" font-weight="700">현재</text>\n'
    ly_start = mt + 6
    for i, p in enumerate(paths):
        c = p.get('color', '#7c6af7')
        lx = width - mr + 6
        ly = ly_start + i * 18
        svg += f'<rect x="{lx}" y="{ly}" width="10" height="10" rx="2" fill="{c}"/>\n'
        svg += f'<text x="{lx+14}" y="{ly+9}" fill="var(--text-sec)" font-size="10">{p["name"]}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_rebased_price(title, datasets, width=600, height=280, sec=0):
    """Peer 수정주가 리베이스 차트. 기준일=100 정규화."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not datasets or not any(d['values'] for d in datasets):
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    max_len = max(len(d['values']) for d in datasets)
    all_vals = [v for d in datasets for v in d['values']]
    v_min, v_max = min(all_vals), max(all_vals)
    v_pad = max((v_max - v_min) * 0.1, 5)
    v_lo, v_hi = v_min - v_pad, v_max + v_pad
    ml, mr, mt, mb = 50, 90, 30, 30
    cw, ch = width - ml - mr, height - mt - mb

    def sx(i): return ml + i / max(max_len - 1, 1) * cw
    def sy(v): return mt + (1 - (v - v_lo) / (v_hi - v_lo)) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    svg += f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    y_ticks = 5
    for i in range(y_ticks + 1):
        v = v_lo + (v_hi - v_lo) * i / y_ticks
        yy = sy(v)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{v:.0f}</text>\n'
    if v_lo <= 100 <= v_hi:
        y100 = sy(100)
        svg += f'<line x1="{ml}" y1="{y100:.1f}" x2="{ml+cw}" y2="{y100:.1f}" stroke="var(--purple, #7c6af7)" stroke-width="1.2" stroke-dasharray="6,3"/>\n'
        svg += f'<text x="{ml+cw+4}" y="{y100+4:.1f}" fill="var(--purple, #7c6af7)" font-size="10" font-weight="600">100</text>\n'
    for d in datasets:
        vals = d['values']
        c = d.get('color', '#7c6af7')
        if len(vals) < 2:
            continue
        pts = ' '.join(f'{sx(i):.1f},{sy(v):.1f}' for i, v in enumerate(vals))
        svg += f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="1.8"/>\n'
        last_x, last_y = sx(len(vals) - 1), sy(vals[-1])
        svg += f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.5" fill="{c}"/>\n'
        svg += f'<text x="{last_x+8:.1f}" y="{last_y+4:.1f}" fill="{c}" font-size="10" font-weight="600">{d["name"]} {vals[-1]:.0f}</text>\n'
    for i, d in enumerate(datasets):
        c = d.get('color', '#7c6af7')
        lx = width - mr + 6
        ly = mt + 4 + i * 16
        svg += f'<rect x="{lx}" y="{ly}" width="10" height="10" rx="2" fill="{c}"/>\n'
        svg += f'<text x="{lx+14}" y="{ly+9}" fill="var(--text-sec)" font-size="9">{d["name"]}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_candlestick(title, data, width=600, height=280, sec=0):
    """캔들스틱 주가 차트. data = [(date_label, open, high, low, close), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not data:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 55, 20, 30, 40
    cw, ch = width - ml - mr, height - mt - mb
    n = len(data)
    all_highs = [d[2] for d in data]
    all_lows = [d[3] for d in data]
    v_min, v_max = min(all_lows), max(all_highs)
    v_pad = max((v_max - v_min) * 0.08, 1)
    v_lo, v_hi = v_min - v_pad, v_max + v_pad
    bar_w = max(cw / max(n, 1) * 0.6, 2)
    gap = cw / max(n, 1)

    def sx(i): return ml + gap * i + gap / 2
    def sy(v): return mt + (1 - (v - v_lo) / (v_hi - v_lo)) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(6):
        v = v_lo + (v_hi - v_lo) * i / 5
        yy = sy(v)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{v:,.0f}</text>\n'
    for i, (lbl, o, h, l, c) in enumerate(data):
        cx = sx(i)
        bullish = c >= o
        color = "var(--positive, #0d9488)" if bullish else "var(--negative, #dc2626)"
        body_top = sy(max(o, c))
        body_bot = sy(min(o, c))
        body_h = max(body_bot - body_top, 1)
        svg += f'<line x1="{cx:.1f}" y1="{sy(h):.1f}" x2="{cx:.1f}" y2="{sy(l):.1f}" stroke="{color}" stroke-width="1"/>\n'
        svg += f'<rect x="{cx - bar_w/2:.1f}" y="{body_top:.1f}" width="{bar_w:.1f}" height="{body_h:.1f}" fill="{color}" rx="1"/>\n'
    step = max(1, n // 8)
    for i in range(0, n, step):
        svg += f'<text x="{sx(i):.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{data[i][0]}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_boxplot(title, datasets, width=600, height=260, sec=0):
    """박스플롯. datasets = [(name, [min, q1, median, q3, max], color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not datasets:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 55, 20, 30, 40
    cw, ch = width - ml - mr, height - mt - mb
    n = len(datasets)
    all_vals = [v for _, vals, _ in datasets for v in vals]
    v_min, v_max = min(all_vals), max(all_vals)
    v_pad = max((v_max - v_min) * 0.1, 1)
    v_lo, v_hi = v_min - v_pad, v_max + v_pad
    box_h = ch / max(n, 1) * 0.6
    gap = ch / max(n, 1)

    def sx(v): return ml + (v - v_lo) / (v_hi - v_lo) * cw
    def sy(i): return mt + gap * i + gap / 2

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(6):
        v = v_lo + (v_hi - v_lo) * i / 5
        xx = sx(v)
        svg += f'<line x1="{xx:.1f}" y1="{mt}" x2="{xx:.1f}" y2="{mt+ch}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{xx:.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{v:,.1f}</text>\n'
    for i, (name, vals, color) in enumerate(datasets):
        mn, q1, med, q3, mx = vals
        cy = sy(i)
        svg += f'<line x1="{sx(mn):.1f}" y1="{cy:.1f}" x2="{sx(mx):.1f}" y2="{cy:.1f}" stroke="{color}" stroke-width="1"/>\n'
        svg += f'<line x1="{sx(mn):.1f}" y1="{cy-box_h/4:.1f}" x2="{sx(mn):.1f}" y2="{cy+box_h/4:.1f}" stroke="{color}" stroke-width="1"/>\n'
        svg += f'<line x1="{sx(mx):.1f}" y1="{cy-box_h/4:.1f}" x2="{sx(mx):.1f}" y2="{cy+box_h/4:.1f}" stroke="{color}" stroke-width="1"/>\n'
        svg += f'<rect x="{sx(q1):.1f}" y="{cy-box_h/2:.1f}" width="{sx(q3)-sx(q1):.1f}" height="{box_h:.1f}" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="1.5" rx="2"/>\n'
        svg += f'<line x1="{sx(med):.1f}" y1="{cy-box_h/2:.1f}" x2="{sx(med):.1f}" y2="{cy+box_h/2:.1f}" stroke="{color}" stroke-width="2"/>\n'
        svg += f'<text x="{ml-8}" y="{cy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{name}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_bullet(title, items, width=600, height=None, sec=0):
    """불릿 그래프. items = [(label, actual, target, ranges), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not items:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    n = len(items)
    row_h = 40
    if height is None:
        height = 30 + n * row_h + 20
    ml, mr, mt = 100, 20, 30
    cw = width - ml - mr

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (label, actual, target, ranges) in enumerate(items):
        cy = mt + i * row_h + row_h / 2
        max_val = max(r[0] for r in ranges) if ranges else max(actual, target)
        svg += f'<text x="{ml-8}" y="{cy+4:.1f}" fill="var(--text)" font-size="11" text-anchor="end">{label}</text>\n'
        for rng_max, rng_color in ranges:
            rw = rng_max / max_val * cw
            svg += f'<rect x="{ml}" y="{cy-12:.1f}" width="{rw:.1f}" height="24" fill="{rng_color}" fill-opacity="0.3" rx="2"/>\n'
        aw = actual / max_val * cw
        svg += f'<rect x="{ml}" y="{cy-6:.1f}" width="{aw:.1f}" height="12" fill="var(--text)" rx="2"/>\n'
        tx = ml + target / max_val * cw
        svg += f'<line x1="{tx:.1f}" y1="{cy-14:.1f}" x2="{tx:.1f}" y2="{cy+14:.1f}" stroke="var(--negative, #dc2626)" stroke-width="2.5"/>\n'
    svg += '</svg></div>\n'
    return svg


def svg_gantt(title, tasks, width=600, height=None, sec=0):
    """간트 차트. tasks = [(name, start_x, duration, color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not tasks:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    n = len(tasks)
    row_h = 32
    if height is None:
        height = 30 + n * row_h + 30
    ml, mr, mt, mb = 110, 20, 30, 30
    cw = width - ml - mr
    max_end = max(t[1] + t[2] for t in tasks)

    def sx(v): return ml + v / max(max_end, 1) * cw

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(6):
        v = max_end * i / 5
        xx = sx(v)
        svg += f'<line x1="{xx:.1f}" y1="{mt}" x2="{xx:.1f}" y2="{mt + n*row_h}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{xx:.1f}" y="{mt + n*row_h + 16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{v:.0f}</text>\n'
    for i, (name, start, dur, color) in enumerate(tasks):
        cy = mt + i * row_h + row_h / 2
        svg += f'<text x="{ml-8}" y="{cy+4:.1f}" fill="var(--text)" font-size="11" text-anchor="end">{name}</text>\n'
        bx = sx(start)
        bw = sx(start + dur) - bx
        svg += f'<rect x="{bx:.1f}" y="{cy-10:.1f}" width="{bw:.1f}" height="20" fill="{color}" rx="4" fill-opacity="0.85"/>\n'
    svg += '</svg></div>\n'
    return svg


def svg_pareto(title, labels, values, width=600, height=280, sec=0):
    """Pareto 차트. 내림차순 바 + 누적 % 라인 + 80% 참조선."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not labels or not values:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    paired = sorted(zip(values, labels), reverse=True)
    values = [p[0] for p in paired]
    labels = [p[1] for p in paired]
    total = sum(values)
    cumul = []
    s = 0
    for v in values:
        s += v
        cumul.append(s / total * 100 if total else 0)
    ml, mr, mt, mb = 55, 50, 30, 50
    cw, ch = width - ml - mr, height - mt - mb
    n = len(labels)
    v_max = max(values)
    bar_w = cw / max(n, 1) * 0.7
    gap = cw / max(n, 1)

    def sx(i): return ml + gap * i + gap / 2
    def sy_bar(v): return mt + (1 - v / v_max) * ch
    def sy_pct(p): return mt + (1 - p / 100) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(6):
        v = v_max * i / 5
        yy = sy_bar(v)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{v:,.0f}</text>\n'
    for i in range(0, 101, 20):
        yy = sy_pct(i)
        svg += f'<text x="{ml+cw+8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10">{i}%</text>\n'
    y80 = sy_pct(80)
    svg += f'<line x1="{ml}" y1="{y80:.1f}" x2="{ml+cw}" y2="{y80:.1f}" stroke="var(--negative, #dc2626)" stroke-width="1" stroke-dasharray="5,3"/>\n'
    svg += f'<text x="{ml+cw+8}" y="{y80+4:.1f}" fill="var(--negative, #dc2626)" font-size="10" font-weight="600">80%</text>\n'
    for i, v in enumerate(values):
        cx = sx(i)
        yy = sy_bar(v)
        svg += f'<rect x="{cx - bar_w/2:.1f}" y="{yy:.1f}" width="{bar_w:.1f}" height="{mt+ch-yy:.1f}" fill="var(--purple, #7c6af7)" fill-opacity="0.7" rx="2"/>\n'
    pts = ' '.join(f'{sx(i):.1f},{sy_pct(cumul[i]):.1f}' for i in range(n))
    svg += f'<polyline points="{pts}" fill="none" stroke="var(--negative, #dc2626)" stroke-width="2"/>\n'
    for i in range(n):
        svg += f'<circle cx="{sx(i):.1f}" cy="{sy_pct(cumul[i]):.1f}" r="3" fill="var(--negative, #dc2626)"/>\n'
    for i, lbl in enumerate(labels):
        svg += f'<text x="{sx(i):.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{lbl[:8]}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_bump(title, labels, datasets, width=600, height=280, sec=0):
    """범프 차트(순위 변동). datasets = [(name, [rank1, rank2, ...], color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not datasets:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 80, 80, 30, 40
    cw, ch = width - ml - mr, height - mt - mb
    n_periods = len(labels) if labels else max(len(d[1]) for d in datasets)
    max_rank = max(max(d[1]) for d in datasets)

    def sx(i): return ml + i / max(n_periods - 1, 1) * cw
    def sy(r): return mt + (r - 1) / max(max_rank - 1, 1) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, lbl in enumerate(labels):
        svg += f'<text x="{sx(i):.1f}" y="{mt-8}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{lbl}</text>\n'
    for r in range(1, max_rank + 1):
        yy = sy(r)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-10}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">#{r}</text>\n'
    for name, ranks, color in datasets:
        pts = ' '.join(f'{sx(i):.1f},{sy(r):.1f}' for i, r in enumerate(ranks))
        svg += f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5"/>\n'
        for i, r in enumerate(ranks):
            svg += f'<circle cx="{sx(i):.1f}" cy="{sy(r):.1f}" r="4" fill="{color}"/>\n'
        last_y = sy(ranks[-1])
        svg += f'<text x="{ml+cw+8}" y="{last_y+4:.1f}" fill="{color}" font-size="10" font-weight="600">{name}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_sparkline(values, width=120, height=30, color='#7c6af7'):
    """미니 인라인 스파크라인. chart-box 래핑 없이 순수 SVG만 반환."""
    if not values or len(values) < 2:
        return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"></svg>'
    v_min, v_max = min(values), max(values)
    v_range = v_max - v_min if v_max != v_min else 1
    pad = 2

    def sx(i): return pad + i / (len(values) - 1) * (width - 2 * pad)
    def sy(v): return pad + (1 - (v - v_min) / v_range) * (height - 2 * pad)

    pts = ' '.join(f'{sx(i):.1f},{sy(v):.1f}' for i, v in enumerate(values))
    svg = f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"/>'
    svg += f'<circle cx="{sx(len(values)-1):.1f}" cy="{sy(values[-1]):.1f}" r="2" fill="{color}"/>'
    svg += '</svg>'
    return svg


def svg_lollipop(title, labels, values, width=600, height=None, sec=0, color='#7c6af7'):
    """로리팝 차트. 얇은 라인 + 원 끝점. 수평 배치."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not labels or not values:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    n = len(labels)
    row_h = 28
    if height is None:
        height = 30 + n * row_h + 20
    ml, mr, mt = 100, 30, 30
    cw = width - ml - mr
    v_max = max(abs(v) for v in values) if values else 1

    def sx(v): return ml + v / v_max * cw

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (lbl, val) in enumerate(zip(labels, values)):
        cy = mt + i * row_h + row_h / 2
        svg += f'<text x="{ml-8}" y="{cy+4:.1f}" fill="var(--text)" font-size="11" text-anchor="end">{lbl}</text>\n'
        end_x = sx(val)
        svg += f'<line x1="{ml}" y1="{cy:.1f}" x2="{end_x:.1f}" y2="{cy:.1f}" stroke="{color}" stroke-width="2"/>\n'
        svg += f'<circle cx="{end_x:.1f}" cy="{cy:.1f}" r="5" fill="{color}"/>\n'
        svg += f'<text x="{end_x+10:.1f}" y="{cy+4:.1f}" fill="var(--text-sec)" font-size="10">{val:,.1f}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_histogram(title, values, bins=10, width=600, height=260, sec=0, color='#7c6af7'):
    """히스토그램. values를 bins개로 나눠서 빈도 막대."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not values:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    v_min, v_max = min(values), max(values)
    if v_min == v_max:
        v_max = v_min + 1
    bin_w = (v_max - v_min) / bins
    counts = [0] * bins
    for v in values:
        idx = min(int((v - v_min) / bin_w), bins - 1)
        counts[idx] += 1
    c_max = max(counts) if counts else 1
    ml, mr, mt, mb = 55, 20, 30, 40
    cw, ch = width - ml - mr, height - mt - mb
    bar_w = cw / bins

    def sx(i): return ml + i * bar_w
    def sy(c): return mt + (1 - c / c_max) * ch

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(6):
        c = c_max * i / 5
        yy = sy(c)
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-8}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{c:.0f}</text>\n'
    for i, c in enumerate(counts):
        yy = sy(c)
        svg += f'<rect x="{sx(i):.1f}" y="{yy:.1f}" width="{bar_w-1:.1f}" height="{mt+ch-yy:.1f}" fill="{color}" fill-opacity="0.75" rx="1"/>\n'
    step = max(1, bins // 6)
    for i in range(0, bins + 1, step):
        v = v_min + bin_w * i
        xx = ml + i * bar_w
        svg += f'<text x="{xx:.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{v:,.1f}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_slope(title, items, width=400, height=300, sec=0):
    """슬로프 차트. items = [(name, val_left, val_right, color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not items:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 100, 100, 40, 20
    cw, ch = width - ml - mr, height - mt - mb
    all_vals = [v for _, vl, vr, _ in items for v in (vl, vr)]
    v_min, v_max = min(all_vals), max(all_vals)
    v_pad = max((v_max - v_min) * 0.1, 1)
    v_lo, v_hi = v_min - v_pad, v_max + v_pad

    def sy(v): return mt + (1 - (v - v_lo) / (v_hi - v_lo)) * ch
    x_left, x_right = ml, ml + cw

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<line x1="{x_left}" y1="{mt}" x2="{x_left}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    svg += f'<line x1="{x_right}" y1="{mt}" x2="{x_right}" y2="{mt+ch}" stroke="var(--border)" stroke-width="1"/>\n'
    for name, vl, vr, color in items:
        yl, yr = sy(vl), sy(vr)
        svg += f'<line x1="{x_left}" y1="{yl:.1f}" x2="{x_right}" y2="{yr:.1f}" stroke="{color}" stroke-width="2"/>\n'
        svg += f'<circle cx="{x_left}" cy="{yl:.1f}" r="4" fill="{color}"/>\n'
        svg += f'<circle cx="{x_right}" cy="{yr:.1f}" r="4" fill="{color}"/>\n'
        svg += f'<text x="{x_left-8}" y="{yl+4:.1f}" fill="{color}" font-size="10" text-anchor="end">{name} {vl:,.1f}</text>\n'
        svg += f'<text x="{x_right+8}" y="{yr+4:.1f}" fill="{color}" font-size="10">{name} {vr:,.1f}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_tornado(title, labels, left_values, right_values, width=600, height=None, sec=0):
    """나비/토네이도 차트. 중앙축 기준 좌(Bear) + 우(Bull)."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not labels:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    n = len(labels)
    row_h = 30
    if height is None:
        height = 30 + n * row_h + 20
    ml, mr, mt = 20, 20, 30
    cw = width - ml - mr
    cx_mid = ml + cw / 2
    half_w = cw / 2 - 40
    v_max = max(max(abs(v) for v in left_values), max(abs(v) for v in right_values)) if left_values and right_values else 1

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<line x1="{cx_mid}" y1="{mt}" x2="{cx_mid}" y2="{mt + n * row_h}" stroke="var(--border)" stroke-width="1"/>\n'
    for i, lbl in enumerate(labels):
        cy = mt + i * row_h + row_h / 2
        lv = abs(left_values[i])
        rv = abs(right_values[i])
        lw = lv / v_max * half_w
        svg += f'<rect x="{cx_mid - 40 - lw:.1f}" y="{cy-10:.1f}" width="{lw:.1f}" height="20" fill="var(--negative, #dc2626)" fill-opacity="0.7" rx="2"/>\n'
        svg += f'<text x="{cx_mid - 40 - lw - 4:.1f}" y="{cy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{lv:,.1f}</text>\n'
        rw = rv / v_max * half_w
        svg += f'<rect x="{cx_mid + 40:.1f}" y="{cy-10:.1f}" width="{rw:.1f}" height="20" fill="var(--positive, #0d9488)" fill-opacity="0.7" rx="2"/>\n'
        svg += f'<text x="{cx_mid + 40 + rw + 4:.1f}" y="{cy+4:.1f}" fill="var(--text-sec)" font-size="10">{rv:,.1f}</text>\n'
        svg += f'<text x="{cx_mid}" y="{cy+4:.1f}" fill="var(--text)" font-size="11" text-anchor="middle" font-weight="600">{lbl}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_treemap(title, items, width=600, height=400, sec=0):
    """트리맵. items = [(label, value, color), ...]. squarified 단순화."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not items:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    items = sorted(items, key=lambda x: x[1], reverse=True)
    total = sum(v for _, v, _ in items)
    if total <= 0:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 10, 10, 30, 10
    tw, th = width - ml - mr, height - mt - mb

    rects = []
    remaining = list(items)
    rx, ry, rw, rh = ml, mt, tw, th
    horizontal = rw >= rh
    for i, (lbl, val, color) in enumerate(remaining):
        frac = val / total if total > 0 else 0
        if i == len(remaining) - 1:
            rects.append((lbl, val, color, rx, ry, rw, rh))
        else:
            if horizontal:
                w = rw * frac / (sum(v for _, v, _ in remaining[i:]) / total) if total > 0 else rw
                w = min(w, rw)
                rects.append((lbl, val, color, rx, ry, w, rh))
                rx += w
                rw -= w
            else:
                h = rh * frac / (sum(v for _, v, _ in remaining[i:]) / total) if total > 0 else rh
                h = min(h, rh)
                rects.append((lbl, val, color, rx, ry, rw, h))
                ry += h
                rh -= h
            horizontal = rw >= rh

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for lbl, val, color, bx, by, bw, bh in rects:
        svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{max(bw-1,0):.1f}" height="{max(bh-1,0):.1f}" fill="{color}" fill-opacity="0.75" stroke="var(--bg, #0d0d1a)" stroke-width="2" rx="3"/>\n'
        pct = val / total * 100
        if bw > 40 and bh > 24:
            fs = min(12, max(10, bw / 8))
            svg += f'<text x="{bx + bw/2:.1f}" y="{by + bh/2 - 2:.1f}" fill="var(--text)" font-size="{fs:.0f}" text-anchor="middle" font-weight="600">{lbl}</text>\n'
            svg += f'<text x="{bx + bw/2:.1f}" y="{by + bh/2 + 12:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{pct:.1f}%</text>\n'
        elif bw > 24 and bh > 16:
            svg += f'<text x="{bx + bw/2:.1f}" y="{by + bh/2 + 4:.1f}" fill="var(--text)" font-size="10" text-anchor="middle">{lbl[:4]}</text>\n'
    svg += '</svg></div>\n'
    return svg


# ═══════════════════════════════════════════════════════════════════════
# TIER 3 — ADVANCED (5종)
# ═══════════════════════════════════════════════════════════════════════

def svg_sankey(title, flows, width=600, height=350, sec=0):
    """Sankey 다이어그램. flows = [(from, to, value, color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not flows:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 20, 20, 30, 20
    cw, ch = width - ml - mr, height - mt - mb
    node_w = 18
    x_left, x_right = ml, ml + cw - node_w

    from_nodes: dict[str, float] = {}
    to_nodes: dict[str, float] = {}
    for f, t, v, _ in flows:
        from_nodes[f] = from_nodes.get(f, 0) + v
        to_nodes[t] = to_nodes.get(t, 0) + v
    total_left = sum(from_nodes.values())
    total_right = sum(to_nodes.values())

    gap = 4
    left_positions: dict[str, tuple[float, float]] = {}
    y = mt
    for name, val in from_nodes.items():
        h = val / max(total_left, 1) * (ch - gap * (len(from_nodes) - 1))
        left_positions[name] = (y, h)
        y += h + gap

    right_positions: dict[str, tuple[float, float]] = {}
    y = mt
    for name, val in to_nodes.items():
        h = val / max(total_right, 1) * (ch - gap * (len(to_nodes) - 1))
        right_positions[name] = (y, h)
        y += h + gap

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'

    left_offsets = {k: v[0] for k, v in left_positions.items()}
    right_offsets = {k: v[0] for k, v in right_positions.items()}
    for f, t, v, color in flows:
        lh = v / max(total_left, 1) * (ch - gap * (len(from_nodes) - 1))
        rh = v / max(total_right, 1) * (ch - gap * (len(to_nodes) - 1))
        y1 = left_offsets[f]
        y2 = right_offsets[t]
        x1 = x_left + node_w
        x2 = x_right
        cp = (x1 + x2) / 2
        svg += f'<path d="M{x1},{y1:.1f} C{cp},{y1:.1f} {cp},{y2:.1f} {x2},{y2:.1f} L{x2},{y2+rh:.1f} C{cp},{y2+rh:.1f} {cp},{y1+lh:.1f} {x1},{y1+lh:.1f} Z" fill="{color}" fill-opacity="0.35"/>\n'
        left_offsets[f] += lh
        right_offsets[t] += rh

    for name, (ny, nh) in left_positions.items():
        svg += f'<rect x="{x_left}" y="{ny:.1f}" width="{node_w}" height="{nh:.1f}" fill="var(--purple, #7c6af7)" rx="3"/>\n'
        svg += f'<text x="{x_left + node_w + 6}" y="{ny + nh/2 + 4:.1f}" fill="var(--text)" font-size="11" font-weight="600">{name}</text>\n'
    for name, (ny, nh) in right_positions.items():
        svg += f'<rect x="{x_right}" y="{ny:.1f}" width="{node_w}" height="{nh:.1f}" fill="var(--purple, #7c6af7)" rx="3"/>\n'
        svg += f'<text x="{x_right - 6}" y="{ny + nh/2 + 4:.1f}" fill="var(--text)" font-size="11" text-anchor="end" font-weight="600">{name}</text>\n'

    svg += '</svg></div>\n'
    return svg


def svg_waffle(title, items, width=400, height=400, sec=0, grid=10):
    """와플 차트. 10x10 격자, 각 셀 = 1%. items = [(label, pct, color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not items:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 10, 10, 30, 50
    tw, th = width - ml - mr, height - mt - mb
    cell_w = tw / grid
    cell_h = th / grid
    total_cells = grid * grid

    cell_colors: list[str] = []
    for label, pct, color in items:
        n_cells = round(pct / 100 * total_cells)
        cell_colors.extend([color] * n_cells)
    while len(cell_colors) < total_cells:
        cell_colors.append('var(--border)')

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(total_cells):
        row = i // grid
        col = i % grid
        x = ml + col * cell_w
        y = mt + row * cell_h
        c = cell_colors[i] if i < len(cell_colors) else 'var(--border)'
        svg += f'<rect x="{x+1:.1f}" y="{y+1:.1f}" width="{cell_w-2:.1f}" height="{cell_h-2:.1f}" fill="{c}" fill-opacity="0.8" rx="3"/>\n'
    lx = ml
    ly = height - mb + 14
    for label, pct, color in items:
        svg += f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{color}"/>\n'
        svg += f'<text x="{lx+16}" y="{ly+10}" fill="var(--text-sec)" font-size="10">{label} ({pct:.0f}%)</text>\n'
        lx += len(label) * 7 + 60
        if lx > width - mr - 40:
            lx = ml
            ly += 16
    svg += '</svg></div>\n'
    return svg


def svg_gauge(title, value, max_val=100, width=300, height=200, sec=0):
    """게이지 차트. 반원형 달성도."""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    cx, cy = width / 2, height - 20
    r = min(cx - 20, cy - 30)
    ratio = min(max(value / max_val, 0), 1)
    angle = math.pi * (1 - ratio)

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<path d="M{cx-r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 0 1 {cx+r:.1f},{cy:.1f}" fill="none" stroke="var(--border)" stroke-width="20" stroke-linecap="round"/>\n'
    if ratio > 0:
        end_x = cx + r * math.cos(angle)
        end_y = cy - r * math.sin(angle)
        large_arc = 1 if ratio > 0.5 else 0
        if ratio < 0.33:
            arc_color = "var(--negative, #dc2626)"
        elif ratio < 0.67:
            arc_color = "#f59e0b"
        else:
            arc_color = "var(--positive, #0d9488)"
        svg += f'<path d="M{cx-r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 {large_arc} 1 {end_x:.1f},{end_y:.1f}" fill="none" stroke="{arc_color}" stroke-width="20" stroke-linecap="round"/>\n'
    svg += f'<text x="{cx}" y="{cy-r/3:.1f}" fill="var(--text)" font-size="28" text-anchor="middle" font-weight="700">{value:,.0f}</text>\n'
    svg += f'<text x="{cx}" y="{cy-r/3+20:.1f}" fill="var(--text-sec)" font-size="12" text-anchor="middle">/ {max_val:,.0f}</text>\n'
    svg += f'<text x="{cx-r-5:.1f}" y="{cy+16:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">0</text>\n'
    svg += f'<text x="{cx+r+5:.1f}" y="{cy+16:.1f}" fill="var(--text-sec)" font-size="10">{max_val:,.0f}</text>\n'
    svg += '</svg></div>\n'
    return svg


def svg_marimekko(title, categories, width=600, height=350, sec=0):
    """Marimekko. categories = [(name, width_val, [(seg, val, color), ...]), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not categories:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    ml, mr, mt, mb = 40, 20, 30, 50
    cw, ch = width - ml - mr, height - mt - mb
    total_w = sum(c[1] for c in categories)
    if total_w <= 0:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i in range(0, 101, 25):
        yy = mt + (1 - i / 100) * ch
        svg += f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+cw}" y2="{yy:.1f}" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>\n'
        svg += f'<text x="{ml-6}" y="{yy+4:.1f}" fill="var(--text-sec)" font-size="10" text-anchor="end">{i}%</text>\n'

    x = ml
    for name, w_val, segments in categories:
        col_w = w_val / total_w * cw
        seg_total = sum(s[1] for s in segments) if segments else 1
        y = mt
        for seg_name, seg_val, seg_color in segments:
            seg_h = seg_val / seg_total * ch if seg_total > 0 else 0
            svg += f'<rect x="{x+1:.1f}" y="{y:.1f}" width="{col_w-2:.1f}" height="{seg_h:.1f}" fill="{seg_color}" fill-opacity="0.8" rx="1"/>\n'
            if seg_h > 16 and col_w > 30:
                svg += f'<text x="{x + col_w/2:.1f}" y="{y + seg_h/2 + 4:.1f}" fill="var(--text)" font-size="10" text-anchor="middle">{seg_name}</text>\n'
            y += seg_h
        svg += f'<text x="{x + col_w/2:.1f}" y="{mt+ch+16}" fill="var(--text-sec)" font-size="10" text-anchor="middle">{name}</text>\n'
        pct = w_val / total_w * 100
        svg += f'<text x="{x + col_w/2:.1f}" y="{mt+ch+28}" fill="var(--text-sec)" font-size="9" text-anchor="middle">({pct:.0f}%)</text>\n'
        x += col_w
    svg += '</svg></div>\n'
    return svg


def svg_pictogram(title, items, width=600, height=None, sec=0):
    """픽토그램. items = [(label, count, symbol, color), ...]"""
    ftitle = f"도표 {fig_num(sec)}. {title}" if sec else title
    if not items:
        return f'<div class="chart-box"><div class="chart-title">{ftitle}</div><p style="color:var(--text-sec)">데이터 없음</p></div>'
    n = len(items)
    max_count = max(it[1] for it in items) if items else 1
    cols = min(max_count, 20)
    row_h = 36
    if height is None:
        height = 30 + n * row_h + 10
    ml, mr, mt = 100, 20, 30
    sym_size = min(16, (width - ml - mr) / max(cols, 1))

    svg = f'<div class="chart-box"><div class="chart-title">{ftitle}</div>\n'
    svg += f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    for i, (label, count, symbol, color) in enumerate(items):
        cy = mt + i * row_h + row_h / 2
        svg += f'<text x="{ml-8}" y="{cy+4:.1f}" fill="var(--text)" font-size="11" text-anchor="end">{label}</text>\n'
        for j in range(min(count, cols)):
            sx = ml + j * sym_size
            svg += f'<text x="{sx:.1f}" y="{cy+5:.1f}" fill="{color}" font-size="{sym_size:.0f}">{symbol}</text>\n'
        if count > cols:
            svg += f'<text x="{ml + cols * sym_size + 4:.1f}" y="{cy+4:.1f}" fill="var(--text-sec)" font-size="10">+{count - cols}</text>\n'
    svg += '</svg></div>\n'
    return svg
