"""
CUFA Equity Report v2 — 메인 빌드 엔진
config.py → HD건설기계 표준 HTML 보고서 생성

Usage:
    python builder/build.py examples/이노스페이스/config.py
    python builder/build.py examples/HD건설기계/config.py
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

# 프로젝트 루트 기준 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "template"
OUTPUT_DIR = PROJECT_ROOT / "output"

# components.py를 import
sys.path.insert(0, str(TEMPLATE_DIR))
import components as C


# ============================================================
#  config.py 로더
# ============================================================

def load_config(config_path: str) -> ModuleType:
    """config.py를 모듈로 동적 로드."""
    path = Path(config_path).resolve()
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
#  CSS / JS 로더
# ============================================================

def load_css() -> str:
    """style.css + style_extended.css 합쳐서 반환."""
    css = ""
    for name in ("style.css", "style_extended.css"):
        p = TEMPLATE_DIR / name
        if p.exists():
            css += p.read_text(encoding="utf-8") + "\n"
    return css


def load_js() -> str:
    """interactive.js 반환."""
    p = TEMPLATE_DIR / "interactive.js"
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ============================================================
#  헬퍼
# ============================================================

def _fmt(v, unit: str = "") -> str:
    """숫자 포맷."""
    if v is None:
        return "N/A"
    if isinstance(v, float) and v != int(v):
        return f"{v:,.1f}{unit}"
    return f"{int(v):,}{unit}"


def _pct(v) -> str:
    if v is None:
        return "N/A"
    return f"{v:+.1f}%" if v >= 0 else f"{v:.1f}%"


def _esc(text) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ============================================================
#  커버 빌드
# ============================================================

def build_cover(cfg: ModuleType) -> str:
    """HD건설기계 패턴 커버 생성."""
    name = cfg.COMPANY_NAME
    code = cfg.TICKER
    subtitle = getattr(cfg, "SUBTITLE", "")
    opinion = getattr(cfg, "OPINION", "N/R")
    target = getattr(cfg, "TARGET_PRICE", None)
    current = getattr(cfg, "CURRENT_PRICE", 0)
    upside = getattr(cfg, "UPSIDE_PCT", None)

    # 투자포인트 하이라이트 박스
    highlights = ""
    ips = getattr(cfg, "INVESTMENT_POINTS", [])
    for ip in ips:
        chain_text = " → ".join(ip.get("chain", [])[:2])
        highlights += (
            f'<div class="highlight-box">'
            f'<h3>투자포인트 {ip["id"]}. {_esc(ip["title"])}</h3>'
            f'<p>{_esc(ip.get("subtitle", ""))}. {_esc(chain_text)}</p>'
            f"</div>\n"
        )

    # 간이 재무 테이블
    fin = getattr(cfg, "FINANCIALS", {})
    rev = fin.get("revenue", {})
    oi = fin.get("operating_income", {})
    ni = fin.get("net_income", {})
    years = sorted([y for y in rev if isinstance(y, int)]) + sorted(
        [y for y in rev if isinstance(y, str)]
    )
    fin_rows = ""
    if years:
        fin_rows += "<tr><th>항목</th>" + "".join(
            f"<th>{y}</th>" for y in years
        ) + "</tr>\n"
        fin_rows += "<tr><td>매출액(억)</td>" + "".join(
            f"<td>{_fmt(rev.get(y))}</td>" for y in years
        ) + "</tr>\n"
        fin_rows += "<tr><td>영업이익(억)</td>" + "".join(
            f"<td>{_fmt(oi.get(y))}</td>" for y in years
        ) + "</tr>\n"
        fin_rows += "<tr><td>순이익(억)</td>" + "".join(
            f"<td>{_fmt(ni.get(y))}</td>" for y in years
        ) + "</tr>\n"

    # 사이드바 메트릭
    mcap = getattr(cfg, "MARKET_CAP", 0)
    w52h = getattr(cfg, "WEEK52_HIGH", 0)
    w52l = getattr(cfg, "WEEK52_LOW", 0)
    shares = getattr(cfg, "SHARES_OUTSTANDING", 0)
    ratios = getattr(cfg, "RATIOS", {})

    target_html = f"<div class='target'>{_fmt(target)}원</div>" if target else "<div class='target'>N/R</div>"
    upside_html = ""
    if target and current and target > 0:
        up = (target - current) / current * 100
        color = "var(--green)" if up > 0 else "var(--red)"
        upside_html = f'<div style="font-size:12px;color:{color};">현재가 {_fmt(current)}원 대비 {up:+.1f}%</div>'
    elif current:
        upside_html = f'<div style="font-size:12px;color:var(--text-sec);">현재가 {_fmt(current)}원</div>'

    opinion_color = "var(--green)" if opinion == "BUY" else ("var(--red)" if opinion == "SELL" else "var(--text)")

    # 대주주
    shareholders = getattr(cfg, "SHAREHOLDERS", [])
    major_sh = shareholders[0] if shareholders else ("", 0, "")

    # 시나리오
    scenarios = getattr(cfg, "SCENARIOS", {})
    bull_bear_html = ""
    if scenarios:
        bull_p = scenarios.get("bull", {}).get("price", "")
        base_p = scenarios.get("base", {}).get("price", "")
        bear_p = scenarios.get("bear", {}).get("price", "")
        bull_bear_html = f"""
        <div style="margin-top:16px;">
          <div style="font-size:11px;color:var(--text-sec);margin-bottom:4px;">Bull / Base / Bear</div>
          <div style="display:flex;gap:8px;font-size:14px;font-weight:700;">
            <span style="color:var(--green);">{_fmt(bull_p)}</span>
            <span style="color:var(--purple);">{_fmt(base_p)}</span>
            <span style="color:var(--red);">{_fmt(bear_p)}</span>
          </div>
        </div>"""

    # 팀 정보
    team = getattr(cfg, "TEAM_NAME", "CUFA")
    members = getattr(cfg, "TEAM_MEMBERS", [])
    date_str = getattr(cfg, "REPORT_DATE_STR", "")
    author_line = ", ".join(members) if members else team

    metrics = [
        ("현재가", f"{_fmt(current)}원"),
        ("시가총액", f"{_fmt(mcap)}억원"),
        ("52주 최고", f"{_fmt(w52h)}원"),
        ("52주 최저", f"{_fmt(w52l)}원"),
        ("PSR(TTM)", f'{_fmt(ratios.get("psr_ttm"))}배' if ratios.get("psr_ttm") else "N/A"),
        ("PER(TTM)", f'{_fmt(ratios.get("per_ttm"))}배' if ratios.get("per_ttm") else "적자"),
        ("PBR", f'{ratios.get("pbr", 0):.2f}배' if ratios.get("pbr") else "N/A"),
        ("발행주식수", _fmt(shares)),
        ("주요주주", f"{major_sh[0]} {major_sh[1]}%" if major_sh[0] else "N/A"),
    ]

    sidebar_metrics = "\n".join(
        f'<div class="sidebar-metric"><span class="label">{_esc(k)}</span><span class="value">{_esc(v)}</span></div>'
        for k, v in metrics
    )

    return f"""
<div class="cover">
  <div class="cover-main">
    <h1>{_esc(name)}</h1>
    <div class="tagline">{_esc(subtitle)}</div>
    <div class="highlights">
{highlights}
    </div>
    <div class="cover-is">
      <table>
{fin_rows}
      </table>
    </div>
    <div style="margin-top:20px;font-size:12px;color:var(--text-sec);">
      <strong style="color:var(--text);">{_esc(author_line)}</strong> | {_esc(team)} | {_esc(date_str)}
    </div>
  </div>
  <div class="cover-sidebar">
    <div class="rating-box">
      <div class="label">투자의견</div>
      <div class="rating" style="color:{opinion_color};">{_esc(opinion)}</div>
      <div style="font-size:11px;color:var(--text-sec);margin:4px 0;">목표주가</div>
      {target_html}
      {upside_html}
    </div>
{sidebar_metrics}
{bull_bear_html}
  </div>
</div>
"""


# ============================================================
#  목차 빌드
# ============================================================

SECTION_TITLES = [
    (1, "기업 개요"),
    (2, "산업 분석"),
    (3, "투자포인트 ①"),
    (4, "투자포인트 ②"),
    (5, "투자포인트 ③"),
    (6, "재무 분석"),
    (7, "Peer 비교"),
    (8, "실적 추정"),
    (9, "밸류에이션"),
    (10, "리스크 분석"),
    (11, "Appendix"),
]


def build_toc(cfg: ModuleType) -> str:
    """목차."""
    ips = getattr(cfg, "INVESTMENT_POINTS", [])

    titles = list(SECTION_TITLES)
    # IP 타이틀 커스터마이즈
    for ip in ips:
        idx = ip["id"] + 2  # IP1=sec3, IP2=sec4, IP3=sec5
        if idx - 1 < len(titles):
            titles[idx - 1] = (idx, f'투자포인트 {ip["id"]}. {ip["title"]}')

    items = "\n".join(
        f'<div class="toc-item"><a href="#sec{n}">{n}. {_esc(t)}</a></div>'
        for n, t in titles
    )
    return f"""
<div class="toc">
  <div style="font-size:16px;font-weight:700;margin-bottom:12px;color:var(--purple);">목 차</div>
{items}
</div>
"""


# ============================================================
#  Float TOC 빌드
# ============================================================

def build_float_toc(cfg: ModuleType) -> str:
    """우측 Float TOC."""
    ips = getattr(cfg, "INVESTMENT_POINTS", [])
    titles = list(SECTION_TITLES)
    for ip in ips:
        idx = ip["id"] + 2
        if idx - 1 < len(titles):
            titles[idx - 1] = (idx, f'IP{ip["id"]}. {ip["title"][:10]}')

    links = "\n".join(
        f'<a href="#sec{n}">{n}. {_esc(t[:20])}</a>'
        for n, t in titles
    )
    return f'<nav class="float-toc">\n{links}\n</nav>'


# ============================================================
#  섹션 빌드 — 섹션별 콘텐츠 함수
# ============================================================

def _section_wrap(num: int, title: str, content: str, cfg: ModuleType) -> str:
    """섹션 래퍼: subheader + header + content."""
    name = cfg.COMPANY_NAME
    code = cfg.TICKER
    header = C.section_header(num, title, name, code)
    return f'\n<div class="section" id="sec{num}">\n{header}\n{content}\n</div>\n'


def build_sec1_overview(cfg: ModuleType) -> str:
    """1. 기업 개요."""
    name = cfg.COMPANY_NAME
    products = getattr(cfg, "PRODUCTS", [])
    shareholders = getattr(cfg, "SHAREHOLDERS", [])
    launch_history = getattr(cfg, "LAUNCH_HISTORY", [])
    fundraising = getattr(cfg, "FUNDRAISING", [])
    listing = getattr(cfg, "LISTING_DATE", "")
    sector = getattr(cfg, "SECTOR", "")
    market = getattr(cfg, "MARKET", "")

    # 사이드바
    sidebar_kv = [
        ("기업명", name),
        ("시장", f"{market}"),
        ("섹터", sector[:15] if sector else ""),
        ("상장일", listing),
    ]

    # 본문: 회사 소개
    intro = f"""
<p><strong>{_esc(name)}는 {_esc(sector)} 섹터에 속하는 {_esc(market)} 상장 기업이다.</strong>
{_esc(listing)}에 상장하였으며, 현재 시가총액은 {_fmt(cfg.MARKET_CAP)}억원이다.</p>
"""

    # 제품 라인업 테이블
    prod_html = ""
    if products:
        headers = ["제품명", "유형", "단수", "높이(m)", "탑재중량(kg)", "엔진", "상태"]
        rows = []
        for p in products:
            rows.append([
                p.get("name", ""),
                p.get("type", ""),
                str(p.get("stages", "")),
                _fmt(p.get("height_m")) if p.get("height_m") else "-",
                _fmt(p.get("payload_kg")) if p.get("payload_kg") else "-",
                p.get("engine", "")[:30],
                p.get("status", "")[:25],
            ])
        prod_html = C.table(headers, rows, sec=1, title="제품 라인업")

    # 대주주
    sh_html = ""
    if shareholders:
        sh_headers = ["주주명", "지분율(%)", "비고"]
        sh_rows = [[s[0], f"{s[1]:.1f}", s[2]] for s in shareholders]
        sh_html = C.table(sh_headers, sh_rows, sec=1, title="주주 구성")

    # 발사 이력
    launch_html = ""
    if launch_history:
        l_headers = ["일자", "발사체", "발사장", "결과", "비고"]
        l_rows = [[l["date"], l["vehicle"], l["site"], l["result"], l["note"][:30]] for l in launch_history]
        launch_html = C.table(l_headers, l_rows, sec=1, title="발사 이력")

    # 자금조달
    fund_html = ""
    if fundraising:
        f_headers = ["일자", "유형", "금액(억원)", "비고"]
        f_rows = [[f["date"], f["type"], _fmt(f.get("amount")) if f.get("amount") else "-", f.get("note", "")[:30]] for f in fundraising]
        fund_html = C.table(f_headers, f_rows, sec=1, title="자금조달 이력")

    content = C.sidebar_wrap(sidebar_kv, intro + prod_html + sh_html + launch_html + fund_html)
    return _section_wrap(1, "기업 개요", content, cfg)


def build_sec2_industry(cfg: ModuleType) -> str:
    """2. 산업 분석."""
    industry = getattr(cfg, "INDUSTRY", {})
    name = cfg.COMPANY_NAME

    sidebar_kv = [
        ("SLV 시장", f"${industry.get('slv_market_2024', 0)}B"),
        ("CAGR", f"{industry.get('slv_cagr', 0)}%"),
        ("한국 우주예산", f"{_fmt(industry.get('korea_space_budget_2026'))}억"),
    ]

    text = f"""
<p><strong>소형발사체(SLV) 시장은 {industry.get('slv_market_2024', 0)}B에서 {industry.get('slv_market_2030', 0)}B으로
CAGR {industry.get('slv_cagr', 0)}%의 고성장이 전망된다.</strong>
LEO 소형위성이 {_fmt(industry.get('leo_satellites_2030'))}기를 넘어서면서
전용 소형발사체 수요가 급증하고 있다.</p>

<p><strong>한국 우주예산은 2026년 {_fmt(industry.get('korea_space_budget_2026'))}억원으로 처음 1조원을 돌파했다.</strong>
전년 대비 {industry.get('korea_space_budget_yoy', 0)}% 증가로, 정부의 우주 산업 육성 의지가 뚜렷하다.
동사는 한국 유일의 민간 소형발사체 기업으로, 이 예산의 직접 수혜자다.</p>

<p><strong>다만 SpaceX Transporter가 소형위성 발사의 {industry.get('rideshare_market_share', 80)}%를 장악하고 있다.</strong>
가격 경쟁에서 rideshare 대비 10배 이상 비싸지만, 전용 발사체는 특수궤도·신속발사·보안 니치에서 수요가 존재한다.
서방 진영에서 실제로 운용 중인 소형발사체는 Electron과 Alpha 단 {industry.get('operating_western_slv', 2)}종뿐이다.</p>
"""

    # 시장 규모 차트
    chart1 = C.svg_bar(
        "글로벌 SLV 시장 규모 ($B)",
        ["2024", "2026E", "2028E", "2030E"],
        [1.7, 2.2, 2.9, 3.6],
        sec=2,
        unit="$B",
    )

    chart2 = C.svg_bar(
        "한국 우주예산 (조원)",
        ["2024", "2025", "2026"],
        [
            industry.get("korea_space_budget_2025", 9649) / 10000,
            industry.get("korea_space_budget_2025", 9649) / 10000,
            industry.get("korea_space_budget_2026", 11201) / 10000,
        ],
        sec=2,
        unit="조",
    )

    charts = f'<div class="chart-pair">\n<div class="chart-box">{chart1}</div>\n<div class="chart-box">{chart2}</div>\n</div>'

    content = C.sidebar_wrap(sidebar_kv, text + charts)
    return _section_wrap(2, "산업 분석", content, cfg)


def build_sec_ip(cfg: ModuleType, ip_idx: int) -> str:
    """투자포인트 섹션 (3, 4, 5)."""
    ips = getattr(cfg, "INVESTMENT_POINTS", [])
    if ip_idx >= len(ips):
        return ""

    ip = ips[ip_idx]
    sec_num = ip_idx + 3
    title = f'투자포인트 {ip["id"]}. {ip["title"]}'

    sidebar_kv = [
        ("핵심 논지", ip.get("subtitle", "")[:15]),
        ("추론 깊이", f"{len(ip.get('chain', []))}단계"),
    ]

    # 추론 체인
    chain = ip.get("chain", [])
    chain_html = '<div style="margin:16px 0;">'
    for i, step in enumerate(chain):
        arrow = " → " if i < len(chain) - 1 else ""
        chain_html += f'<span style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:6px 10px;display:inline-block;margin:4px;font-size:12px;">{_esc(step)}</span>{arrow}'
    chain_html += "</div>"

    text = f"""
<p><strong>{_esc(ip['title'])} — {_esc(ip.get('subtitle', ''))}</strong></p>
{chain_html}
"""

    # IP별 상세 본문 (확장 가능)
    for step in chain:
        text += f"\n<p>{_esc(step)}</p>\n"

    content = C.sidebar_wrap(sidebar_kv, text)
    return _section_wrap(sec_num, title, content, cfg)


def build_sec6_financial(cfg: ModuleType) -> str:
    """6. 재무 분석."""
    fin = getattr(cfg, "FINANCIALS", {})
    rev = fin.get("revenue", {})
    oi = fin.get("operating_income", {})
    ni = fin.get("net_income", {})
    assets = fin.get("total_assets", {})
    equity = fin.get("stockholders_equity", {})
    cash = fin.get("cash", {})

    years = sorted([y for y in rev if isinstance(y, int)])

    sidebar_kv = [
        ("최근 매출", f"{_fmt(rev.get(years[-1]))}억" if years else "N/A"),
        ("현금", f"{_fmt(cash.get(years[-1]))}억" if years and cash else "N/A"),
    ]

    # 재무 요약 테이블
    headers = ["항목"] + [str(y) for y in years]
    rows = [
        ["매출액"] + [_fmt(rev.get(y)) for y in years],
        ["영업이익"] + [_fmt(oi.get(y)) for y in years],
        ["순이익"] + [_fmt(ni.get(y)) for y in years],
        ["총자산"] + [_fmt(assets.get(y)) for y in years],
        ["자기자본"] + [_fmt(equity.get(y)) for y in years],
        ["현금"] + [_fmt(cash.get(y)) for y in years],
    ]
    tbl = C.table(headers, rows, sec=6, title="재무 요약 (억원)")

    # 매출 차트
    rev_labels = [str(y) for y in years]
    rev_values = [rev.get(y, 0) for y in years]
    chart1 = C.svg_bar("매출액 추이 (억원)", rev_labels, rev_values, sec=6)

    # 순이익 차트
    ni_values = [ni.get(y, 0) for y in years]
    chart2 = C.svg_bar("순이익 추이 (억원)", rev_labels, ni_values, sec=6)

    charts = f'<div class="chart-pair">\n<div class="chart-box">{chart1}</div>\n<div class="chart-box">{chart2}</div>\n</div>'

    # 메트릭 그리드
    ratios = getattr(cfg, "RATIOS", {})
    metrics = C.metric_grid([
        ("PSR(TTM)", f'{_fmt(ratios.get("psr_ttm"))}배', "", ""),
        ("PBR", f'{ratios.get("pbr", 0):.1f}배' if ratios.get("pbr") else "N/A", "", ""),
        ("ROE", f'{ratios.get("roe", 0):.1f}%' if ratios.get("roe") else "N/A", "", "down" if ratios.get("roe", 0) < 0 else "up"),
        ("유동비율", f'{ratios.get("current_ratio", 0):.1f}배' if ratios.get("current_ratio") else "N/A", "", ""),
    ])

    text = f"""
<p><strong>동사의 재무 구조는 전형적인 Pre-revenue 우주기업 패턴을 보인다.</strong>
매출은 미미하나 R&D 투자가 매출의 수십 배에 달하며, 영업적자가 지속되고 있다.
다만 현금 {_fmt(cash.get(years[-1]) if years else 0)}억원과 진행중인 유상증자 825억원으로
최소 2027년까지의 운영자금은 확보될 전망이다.</p>
"""

    content = C.sidebar_wrap(sidebar_kv, text + metrics + tbl + charts)
    return _section_wrap(6, "재무 분석", content, cfg)


def build_sec7_peer(cfg: ModuleType) -> str:
    """7. Peer 비교."""
    peers = getattr(cfg, "PEERS", {})
    if not peers:
        return _section_wrap(7, "Peer 비교", "<p>Peer 데이터 없음</p>", cfg)

    sidebar_kv = [
        ("비교 대상", f"{len(peers)}개사"),
    ]

    headers = ["기업명", "국가", "시총(M$)", "매출(M$)", "PSR", "발사횟수", "성공률(%)"]
    rows = []
    for ticker, p in peers.items():
        rows.append([
            p.get("name", ticker),
            p.get("country", ""),
            _fmt(p.get("market_cap_usd", 0)),
            _fmt(p.get("revenue_usd", 0)),
            f'{p.get("psr", 0):.0f}x',
            str(p.get("launches", 0)),
            f'{p.get("success_rate", 0):.0f}',
        ])
    tbl = C.table(headers, rows, sec=7, title="Peer 비교", src="yfinance, MacroTrends")

    # PSR 비교 차트
    names = [p.get("name", t)[:8] for t, p in peers.items()]
    psrs = [p.get("psr", 0) for p in peers.values()]
    chart = C.svg_hbar("PSR 비교", names, psrs, sec=7)

    text = f"""
<p><strong>동사의 PSR은 Peer 대비 높은 수준이나, Pre-revenue 단계를 감안해야 한다.</strong>
Rocket Lab은 84회 발사 실적과 Neutron 개발로 PSR 58배를 정당화하고 있으며,
Firefly는 Alpha 7회 발사로 PSR 29배에 거래중이다.</p>
"""

    content = C.sidebar_wrap(
        sidebar_kv,
        text + tbl + f'<div class="chart-box">{chart}</div>',
    )
    return _section_wrap(7, "Peer 비교", content, cfg)


def build_sec8_estimates(cfg: ModuleType) -> str:
    """8. 실적 추정."""
    fin = getattr(cfg, "FINANCIALS", {})
    rev = fin.get("revenue", {})
    oi = fin.get("operating_income", {})
    consensus = getattr(cfg, "CONSENSUS", {})

    est_years = [y for y in rev if isinstance(y, str)]  # '2026E', '2027E', ...

    sidebar_kv = [
        ("추정 기간", f"{est_years[0]}~{est_years[-1]}" if est_years else "N/A"),
        ("BEP 전망", f"{consensus.get('bep_year', 'N/A')}"),
    ]

    headers = ["항목"] + [str(y) for y in est_years]
    rows = [
        ["매출액(억)"] + [_fmt(rev.get(y)) for y in est_years],
        ["영업이익(억)"] + [_fmt(oi.get(y)) for y in est_years],
    ]
    tbl = C.table(headers, rows, sec=8, title="실적 추정 요약")

    # 매출 추정 차트
    if est_years:
        labels = [str(y) for y in est_years]
        values = [rev.get(y, 0) for y in est_years]
        chart = C.svg_bar("매출 추정 (억원)", labels, values, sec=8)
    else:
        chart = ""

    text = f"""
<p><strong>본서는 동사의 매출을 발사 횟수 × 발사 단가 기반 P×Q 모델로 추정한다.</strong>
증권사 컨센서스 매출 {_fmt(consensus.get('revenue_2026E'))}억원(2026E)은
6회 발사 성공을 전제하나, 본서는 보수적으로 2회 성공을 가정하였다.</p>
"""

    # 컨센서스 vs CUFA 비교
    if consensus.get("revenue_2026E"):
        comp_text = f"""
<p><strong>CUFA 추정치와 컨센서스의 괴리가 크다.</strong>
컨센서스 {_fmt(consensus.get('revenue_2026E'))}억원 대비 CUFA 추정 {_fmt(rev.get('2026E'))}억원으로
{((rev.get('2026E', 0) / consensus.get('revenue_2026E', 1)) - 1) * 100:+.1f}% 차이가 있다.
이는 발사 성공 횟수 가정의 차이에 기인한다.</p>
"""
    else:
        comp_text = ""

    content = C.sidebar_wrap(sidebar_kv, text + comp_text + tbl + (f'<div class="chart-box">{chart}</div>' if chart else ""))
    return _section_wrap(8, "실적 추정", content, cfg)


def build_sec9_valuation(cfg: ModuleType) -> str:
    """9. 밸류에이션."""
    scenarios = getattr(cfg, "SCENARIOS", {})
    current = getattr(cfg, "CURRENT_PRICE", 0)
    peers = getattr(cfg, "PEERS", {})
    ratios = getattr(cfg, "RATIOS", {})

    sidebar_kv = [
        ("방법론", "PSR + Peer"),
        ("현재가", f"{_fmt(current)}원"),
    ]

    text = f"""
<p><strong>동사는 적자 기업으로 PER/PBR 밸류에이션이 적합하지 않으며, PSR(매출 기반)과 Peer 비교를 주요 방법론으로 사용한다.</strong>
Pre-revenue 우주기업은 발사 성공률과 수주잔고가 밸류에이션의 핵심 드라이버다.</p>
"""

    # 시나리오 그리드
    scenario_html = ""
    if scenarios:
        bull = scenarios.get("bull", {})
        base = scenarios.get("base", {})
        bear = scenarios.get("bear", {})
        scenario_html = C.scenario_grid(
            {k: str(v) for k, v in bull.items()},
            {k: str(v) for k, v in base.items()},
            {k: str(v) for k, v in bear.items()},
        )

    # Football Field — svg_football(title, rows=[(label, lo, hi, color)], current, sec)
    if peers:
        peer_rows = []
        for p in peers.values():
            psr = p.get("psr", 0)
            peer_rows.append((p.get("name", "")[:10], psr * 0.7, psr * 1.3, C.C_PURPLE))
        football = C.svg_football("PSR Football Field", peer_rows, current=ratios.get("psr_ttm", 0) or 0, sec=9)
    else:
        football = ""

    content = C.sidebar_wrap(
        sidebar_kv,
        text + scenario_html + (f'<div class="chart-box">{football}</div>' if football else ""),
    )
    return _section_wrap(9, "밸류에이션", content, cfg)


def build_sec10_risk(cfg: ModuleType) -> str:
    """10. 리스크 분석."""
    risks = getattr(cfg, "RISKS", [])
    kill_conds = getattr(cfg, "KILL_CONDITIONS", [])

    sidebar_kv = [
        ("리스크 수", f"{len(risks)}개"),
        ("Kill Condition", f"{len(kill_conds)}개"),
    ]

    # 리스크 그리드
    risk_items = []
    for r in risks:
        prob = r.get("probability", 50)
        level = "high" if prob >= 60 else ("med" if prob >= 30 else "low")
        risk_items.append((r["name"], level, r.get("description", "")[:60]))
    risk_html = C.risk_grid(risk_items)

    # Kill Conditions 테이블
    kc_html = ""
    if kill_conds:
        kc_headers = ["조건", "현재 상태", "여유", "모니터링"]
        kc_rows = [[kc["condition"], kc["current"], kc["margin"], kc["frequency"]] for kc in kill_conds]
        kc_html = C.table(kc_headers, kc_rows, sec=10, title="Kill Conditions")

    # 리스크 상세
    text = ""
    for r in risks:
        text += f"""
<p><strong>{_esc(r['name'])} (확률 {r.get('probability', 0)}% / 영향도 {r.get('impact', 0)}%)</strong></p>
<p>{_esc(r.get('description', ''))}</p>
<p>대응: {_esc(r.get('mitigation', ''))}</p>
"""

    # 버블 리스크 차트 — svg_bubble_risk(title, risks=[(label, prob, impact, severity)], sec)
    if risks:
        bubble_data = [
            (r["name"][:8], r.get("probability", 50), r.get("impact", 50),
             r.get("probability", 50) * r.get("impact", 50) / 100)
            for r in risks
        ]
        bubble = C.svg_bubble_risk("리스크 매트릭스", bubble_data, sec=10)
    else:
        bubble = ""

    content = C.sidebar_wrap(
        sidebar_kv,
        text + risk_html + kc_html + (f'<div class="chart-box">{bubble}</div>' if bubble else ""),
    )
    return _section_wrap(10, "리스크 분석", content, cfg)


def build_sec11_appendix(cfg: ModuleType) -> str:
    """11. Appendix."""
    fin = getattr(cfg, "FINANCIALS", {})
    backlog = getattr(cfg, "BACKLOG", {})
    launch_sites = getattr(cfg, "LAUNCH_SITES", [])

    sidebar_kv = [
        ("유형", "데이터 레퍼런스"),
    ]

    # 수주잔고
    backlog_html = ""
    if backlog:
        contracts = backlog.get("key_contracts", [])
        if contracts:
            headers = ["고객", "내용", "금액", "연도"]
            rows = [[c["client"][:15], c["content"][:25], str(c.get("value", "-")), str(c.get("year", ""))] for c in contracts]
            backlog_html = C.table(headers, rows, sec=11, title=f"수주잔고 상세 ({_fmt(backlog.get('total_value_krw'))}억원)")

    # 발사장
    site_html = ""
    if launch_sites:
        headers = ["발사장", "위치", "상태", "장점"]
        rows = [[s["name"], s["location"][:15], s["status"][:15], s["advantage"][:20]] for s in launch_sites]
        site_html = C.table(headers, rows, sec=11, title="발사장 인프라")

    # 전체 재무 테이블 (상세)
    rev = fin.get("revenue", {})
    all_years = sorted([y for y in rev if isinstance(y, int)]) + sorted([y for y in rev if isinstance(y, str)])
    full_headers = ["항목"] + [str(y) for y in all_years]
    full_rows = []
    for key_name, label in [
        ("revenue", "매출액"),
        ("cost_of_revenue", "매출원가"),
        ("gross_profit", "매출총이익"),
        ("rnd", "R&D"),
        ("sga", "판관비"),
        ("operating_income", "영업이익"),
        ("net_income", "순이익"),
        ("total_assets", "총자산"),
        ("stockholders_equity", "자기자본"),
        ("cash", "현금"),
        ("total_debt", "총부채"),
    ]:
        data = fin.get(key_name, {})
        if data:
            full_rows.append([label] + [_fmt(data.get(y)) for y in all_years])

    full_tbl = ""
    if full_rows:
        full_tbl = C.table(full_headers, full_rows, sec=11, title="재무제표 상세 (억원)", src="DART, yfinance")

    content = C.sidebar_wrap(sidebar_kv, backlog_html + site_html + full_tbl)
    cls = ' class="section appendix"'
    header = C.section_header(11, "Appendix", cfg.COMPANY_NAME, cfg.TICKER)
    return f'\n<div{cls} id="sec11">\n{header}\n{content}\n</div>\n'


# ============================================================
#  푸터 빌드
# ============================================================

def build_footer(cfg: ModuleType) -> str:
    """푸터 + 면책."""
    team = getattr(cfg, "TEAM_NAME", "CUFA")
    members = getattr(cfg, "TEAM_MEMBERS", [])
    author = ", ".join(members) if members else team
    date_str = getattr(cfg, "REPORT_DATE_STR", "")

    return f"""
<div class="footer">
  <div class="author">{_esc(author)}</div>
  <div class="org">{_esc(team)} | {_esc(date_str)}</div>
  <div class="disclaimer">
    본 보고서는 충북대학교 가치투자학회(CUFA)의 교육·연구 목적으로 작성된 것으로,
    특정 종목에 대한 투자 권유나 조언이 아닙니다.
    보고서에 포함된 분석과 의견은 작성일 기준이며,
    투자 판단의 최종 책임은 투자자 본인에게 있습니다.
    본 보고서의 내용은 신뢰할 수 있는 자료에 기반하였으나 정확성이나 완전성을 보장하지 않습니다.
  </div>
</div>
"""


# ============================================================
#  메인 빌드 함수
# ============================================================

def _load_custom_sections(config_path: str) -> ModuleType | None:
    """config.py 옆에 sections.py가 있으면 로드. 없으면 None."""
    config_dir = Path(config_path).resolve().parent
    sections_path = config_dir / "sections.py"
    if not sections_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("custom_sections", sections_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # components를 sections에서도 쓸 수 있도록 주입 (exec 후, C=None 덮어쓰기 대응)
    mod.C = C
    print(f"Custom sections loaded: {sections_path}")
    return mod


def build_report(config_path: str) -> str:
    """config.py를 읽어 완전한 HTML 보고서를 생성한다."""
    cfg = load_config(config_path)

    # 카운터 초기화
    C._reset_counters()

    css = load_css()
    js = load_js()

    name = cfg.COMPANY_NAME
    code = cfg.TICKER

    # 커스텀 sections 로더: config.py 옆에 sections.py가 있으면 사용
    custom = _load_custom_sections(config_path)

    # 자동 생성 fallback 맵
    auto_builders = {
        1: lambda: build_sec1_overview(cfg),
        2: lambda: build_sec2_industry(cfg),
        3: lambda: build_sec_ip(cfg, 0),
        4: lambda: build_sec_ip(cfg, 1),
        5: lambda: build_sec_ip(cfg, 2),
        6: lambda: build_sec6_financial(cfg),
        7: lambda: build_sec7_peer(cfg),
        8: lambda: build_sec8_estimates(cfg),
        9: lambda: build_sec9_valuation(cfg),
        10: lambda: build_sec10_risk(cfg),
        11: lambda: build_sec11_appendix(cfg),
    }

    def _sec(num: int) -> str:
        """커스텀 섹션이 있으면 우선, 없으면 자동 생성."""
        func_name = f"gen_section{num}"
        if custom and hasattr(custom, func_name):
            return getattr(custom, func_name)()
        return auto_builders[num]()

    # 각 섹션 빌드
    sections = [
        build_cover(cfg),
        build_toc(cfg),
        _sec(1), _sec(2), _sec(3), _sec(4), _sec(5),
        _sec(6), _sec(7), _sec(8), _sec(9), _sec(10), _sec(11),
        build_footer(cfg),
    ]

    body = "\n".join(sections)

    # Float TOC
    float_toc = build_float_toc(cfg)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(name)} ({_esc(code)}) — CUFA 기업분석보고서</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="reading-progress"></div>
{float_toc}
<div class="report">
{body}
</div>
<button class="back-to-top" aria-label="맨 위로">&#8593;</button>
<script>
{js}
</script>
</body>
</html>"""

    return html


# ============================================================
#  CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python builder/build.py <config.py>")
        print("Example: python builder/build.py examples/이노스페이스/config.py")
        sys.exit(1)

    config_path = sys.argv[1]
    print(f"Building report from: {config_path}")

    html = build_report(config_path)

    # config에서 종목명 가져오기
    cfg = load_config(config_path)
    name = cfg.COMPANY_NAME

    # 출력 디렉토리
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{name}_CUFA_보고서.html"

    output_path.write_text(html, encoding="utf-8")
    print(f"Report saved: {output_path}")
    print(f"Size: {len(html.encode('utf-8')):,} bytes")

    # 간단한 통계
    import re
    text_only = re.sub(r'<[^>]+>', '', html)
    text_chars = len(text_only.replace(' ', '').replace('\n', ''))
    svg_count = html.count('<svg ')
    table_count = html.count('<table')

    print(f"Text: {text_chars:,} chars | SVG: {svg_count} | Tables: {table_count}")

    return output_path


if __name__ == "__main__":
    main()
