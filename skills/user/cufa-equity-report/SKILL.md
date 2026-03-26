---
name: cufa-equity-report
description: "CUFA 가치투자학회 기업분석보고서 생성. SMIC(서울대 투자연구회) 레이아웃 정밀 복제 .docx + 퍼플 다크 인터랙티브 .html 동시 생성. 트리거: '기업분석보고서', '보고서 만들어', 'CUFA 보고서', '투자보고서', 'equity research', 'SMIC 스타일', '기업 리서치'. DART+pykrx+FRED+ECOS 데이터 수집 → matplotlib 차트 → python-docx 빌드 → 인터랙티브 HTML."
---

# CUFA 기업분석보고서 생성 스킬

## 워크플로우

```
0. 데이터 수집 — Nexus MCP (기본) or 재무데이터 Excel
   → dart_financial_statements, stocks_market_overview, ecos_search 등
   → MCP에서 못 가져온 건 빈칸 → 찬희님 수동 입력
   → mock 데이터 절대 금지
1. 환경 세팅 (pip install)
2. 마크다운 본문 작성 (75,000자+ 목표)
3. 차트 생성 (matplotlib 라이트+다크 2벌, or 인라인 SVG)
4. 인터랙티브 HTML 빌드 (build_template.py)
5. Evaluator 검증 (자동 채점 → 85점 미만 시 보강)
6. PDF 변환 (LibreOffice, 선택)
```

**데이터 수집 우선순위**: Nexus MCP > pykrx/yfinance 직접 호출 > 재무데이터 Excel > 찬희님 수동 입력
**절대 금지**: mock/더미 데이터로 보고서 생성

## 1. 환경 세팅

```bash
pip install python-docx openpyxl pandas matplotlib pykrx yfinance requests lxml --break-system-packages
# DART/FRED/ECOS API 키는 환경변수에서 읽기
# DART_API_KEY, FRED_API_KEY, ECOS_API_KEY
```

## 2. 프로젝트 구조

```
cufa_report_{종목코드}/
├── data/                  # 수집 데이터
│   ├── financials.xlsx
│   ├── stock_price.csv
│   ├── peer_data.xlsx
│   └── macro.xlsx
├── charts/                # 라이트 테마 차트 (docx용)
│   ├── cover_12m.png
│   ├── fig_1_1.png ~ fig_1_6.png
│   ├── fig_2_1.png ~ fig_2_8.png
│   └── fig_8_1.png
├── charts_dark/           # 다크 테마 차트 (html용)
│   └── (동일 파일명)
├── output/
│   ├── report.docx
│   ├── report.pdf
│   └── report.html
└── src/
    ├── config.py          # 종목 설정, 테마, 상수
    ├── data_collector.py  # API 데이터 수집
    ├── chart_factory.py   # 차트 생성기
    ├── docx_builder.py    # SMIC 레이아웃 docx 빌드
    ├── html_builder.py    # 인터랙티브 HTML 빌드
    └── utils.py           # 유틸리티
```

## 3. config.py — 종목 설정 + 테마 + 상수

```python
import os
from dataclasses import dataclass

# === API 키 ===
DART_API_KEY = os.environ.get('DART_API_KEY', '')
FRED_API_KEY = os.environ.get('FRED_API_KEY', '')
ECOS_API_KEY = os.environ.get('ECOS_API_KEY', '')

# === 종목 설정 (파일럿마다 여기만 수정) ===
TICKER = '042670'
COMPANY_NAME = 'HD현대인프라코어'
COMPANY_NAME_EN = 'HD Hyundai Infracore'
MARKET = 'KOSPI'
SUBTITLE = '보고서 부제를 여기에'  # 예: "Shaheen-ing Oil"

PEERS_KR = {'241560': '두산밥캣'}
PEERS_GLOBAL = {'CAT': 'Caterpillar', '6301.T': 'Komatsu'}

TEAM_NAME = 'CUFA X팀'
TEAM_MEMBERS = ['이름1', '이름2', '이름3']

# === 페이지 설정 (SMIC 역공학, mm 단위) ===
@dataclass
class PageSpec:
    width_mm: float = 210
    height_mm: float = 297
    margin_top_mm: float = 20
    margin_bottom_mm: float = 15
    margin_left_mm: float = 18
    margin_right_mm: float = 18
    header_height_mm: float = 12
    footer_height_mm: float = 10

    @property
    def content_width_mm(self):
        return self.width_mm - self.margin_left_mm - self.margin_right_mm

PAGE = PageSpec()

# === SMIC 2단 레이아웃 비율 ===
SIDEBAR_RATIO = 0.20   # 좌측 사이드노트 20%
BODY_RATIO = 0.78      # 우측 본문 78%
GAP_RATIO = 0.02       # 간격 2%

# === 폰트 사양 (SMIC 역공학) ===
@dataclass
class FontSpec:
    family: str
    size_pt: float
    bold: bool = False
    color_hex: str = '333333'
    line_spacing: float = 1.5

FONTS = {
    'page_header':     FontSpec('맑은 고딕', 8,    False, '666666', 1.0),
    'section_title':   FontSpec('맑은 고딕', 16,   True,  '000000', 1.3),
    'section_subtitle':FontSpec('맑은 고딕', 13,   True,  '000000', 1.3),
    'subsection':      FontSpec('맑은 고딕', 10,   True,  '000000', 1.3),
    'sidebar':         FontSpec('맑은 고딕', 8.5,  True,  '333333', 1.3),
    'body':            FontSpec('맑은 고딕', 9,    False, '333333', 1.5),
    'body_bold':       FontSpec('맑은 고딕', 9,    True,  '000000', 1.5),
    'chart_title':     FontSpec('맑은 고딕', 8,    True,  '000000', 1.0),
    'chart_unit':      FontSpec('맑은 고딕', 7,    False, '999999', 1.0),
    'chart_source':    FontSpec('맑은 고딕', 7,    False, '999999', 1.0),
    'table_header':    FontSpec('맑은 고딕', 8,    True,  'FFFFFF', 1.0),
    'table_data':      FontSpec('맑은 고딕', 8,    False, '333333', 1.0),
    'page_number':     FontSpec('맑은 고딕', 8,    False, '666666', 1.0),
}

# === 재무 테이블 색상 ===
TABLE_COLORS = {
    'header_bg': '333333',
    'header_text': 'FFFFFF',
    'row_even': 'F5F5F5',
    'row_odd': 'FFFFFF',
    'border': 'CCCCCC',
    'negative': 'E63946',
}

# === matplotlib 차트 테마 ===
CHART_LIGHT = {
    'bg': '#FFFFFF',
    'text': '#333333',
    'grid': '#E8E8E8',
    'spine': '#CCCCCC',
    'primary': '#7c6af7',       # 시그니처 퍼플 — 동사
    'secondary': '#4A7FB5',     # 블루 — Peer/비교
    'tertiary': '#2A9D8F',      # 틸 — 보조
    'quaternary': '#F4A261',    # 앰버 — 4번째
    'gray': '#CCCCCC',
    'positive': '#2A9D8F',
    'negative': '#E63946',
}

CHART_DARK = {
    'bg': '#0a0a0a',
    'text': '#e0e0e0',
    'grid': '#1a1a1a',
    'spine': '#333333',
    'primary': '#a78bfa',       # 밝은 퍼플
    'secondary': '#6CB4EE',
    'tertiary': '#4ECDC4',
    'quaternary': '#FFD93D',
    'gray': '#333333',
    'positive': '#4ECDC4',
    'negative': '#FF6B6B',
}

# === HTML 인터랙티브 CSS 변수 ===
HTML_THEME = {
    'bg': '#0a0a0a',
    'surface': '#0f0f0f',
    'surface2': '#141414',
    'border': '#222222',
    'text': '#e0e0e0',
    'text2': '#888888',
    'text3': '#555555',
    'purple': '#7c6af7',
    'purple_light': '#a78bfa',
    'purple_bg': '#12101f',
    'purple_border': '#2d2654',
    'positive': '#4ecdc4',
    'negative': '#ff6b6b',
    'blue': '#6cb4ee',
    'amber': '#ffd93d',
}

# === 도표 번호 체계 ===
# 도표 X-Y. (X=섹션번호, Y=섹션 내 순번)
# 1:산업분석 2:기업분석 3:TP① 4:TP② 5:Plus α 6:매출추정 7:비용추정 8:밸류에이션

# === 서술 규칙 ===
# - 소제목마다 첫 문장 Bold로 주장 선언 → 보통체로 근거 전개
# - 밑줄은 결론 1~2문장에만
# - 단정적 서술체: "~이다" (○), "~할 것으로 판단된다" (×)
# - 경어 미사용
```

## 4. docx_builder.py — SMIC 레이아웃 핵심

```python
"""
SMIC 레이아웃 정밀 복제 docx 빌더.
핵심 구조: 보이지 않는 2열 테이블로 '좌측 사이드노트 + 우측 본문' 구현.
"""

from docx import Document
from docx.shared import Mm, Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from config import PAGE, FONTS, TABLE_COLORS, SIDEBAR_RATIO, BODY_RATIO

# ============================================================
# 유틸리티
# ============================================================

def set_font(run, spec):
    """FontSpec 객체로 run 폰트 설정"""
    run.font.name = spec.family
    run.font.size = Pt(spec.size_pt)
    run.font.bold = spec.bold
    run.font.color.rgb = RGBColor.from_string(spec.color_hex)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:eastAsia'), spec.family)

def set_line_spacing(paragraph, multiplier):
    """줄간격 설정"""
    pPr = paragraph._p.get_or_add_pPr()
    existing = pPr.findall(qn('w:spacing'))
    for e in existing:
        pPr.remove(e)
    spacing = parse_xml(
        f'<w:spacing {nsdecls("w")} '
        f'w:line="{int(240 * multiplier)}" w:lineRule="auto" '
        f'w:before="0" w:after="60"/>'
    )
    pPr.append(spacing)

def remove_table_borders(table):
    """테이블 테두리 완전 제거"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        tbl.insert(0, tblPr)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)

def add_paragraph_border_bottom(paragraph, color='000000', size=4):
    """문단 하단 실선"""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="{size}" w:space="1" w:color="{color}"/>'
        '</w:pBdr>'
    )
    pPr.append(pBdr)

def set_cell_width(cell, width_mm):
    """셀 너비 강제 설정"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcW = parse_xml(
        f'<w:tcW {nsdecls("w")} w:w="{int(width_mm / 25.4 * 1440)}" w:type="dxa"/>'
    )
    existing = tcPr.findall(qn('w:tcW'))
    for e in existing:
        tcPr.remove(e)
    tcPr.append(tcW)

def set_cell_vertical_align(cell, align='top'):
    """셀 수직 정렬"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    vAlign = parse_xml(
        f'<w:vAlign {nsdecls("w")} w:val="{align}"/>'
    )
    tcPr.append(vAlign)

# ============================================================
# 문서 초기화
# ============================================================

def create_document():
    """SMIC 사양 문서 생성"""
    doc = Document()
    
    section = doc.sections[0]
    section.page_width = Mm(PAGE.width_mm)
    section.page_height = Mm(PAGE.height_mm)
    section.top_margin = Mm(PAGE.margin_top_mm)
    section.bottom_margin = Mm(PAGE.margin_bottom_mm)
    section.left_margin = Mm(PAGE.margin_left_mm)
    section.right_margin = Mm(PAGE.margin_right_mm)
    section.header_distance = Mm(8)
    section.footer_distance = Mm(8)
    
    return doc

# ============================================================
# 헤더/푸터
# ============================================================

def setup_header(section, company, ticker, subtitle):
    """
    페이지 헤더:
    ┌─────────────────────────────────────────┐
    │ 기업명 (종목코드) / 부제       [CUFA 로고] │
    │ ───────────────────────────────────── │
    └─────────────────────────────────────────┘
    """
    header = section.header
    header.is_linked_to_previous = False
    
    p = header.paragraphs[0]
    p.clear()
    
    left_text = f'{company} ({ticker}, {subtitle})'
    run = p.add_run(left_text)
    set_font(run, FONTS['page_header'])
    
    # 우측에 CUFA 텍스트
    run2 = p.add_run('\t\tCUFA')
    set_font(run2, FONTS['page_header'])
    run2.font.bold = True
    
    add_paragraph_border_bottom(p, color='CCCCCC', size=4)

def setup_footer(section):
    """
    페이지 푸터:
    │ ───────────────────────────────────── │
    │ CUFA                          [페이지] │
    """
    footer = section.footer
    footer.is_linked_to_previous = False
    
    p = footer.paragraphs[0]
    p.clear()
    
    run = p.add_run('CUFA')
    set_font(run, FONTS['page_number'])
    run.font.bold = True

# ============================================================
# SMIC 2단 레이아웃 — 핵심
# ============================================================

def add_section_title(doc, number, title):
    """
    섹션 대제목: "1. 산업분석" 스타일
    좌측에 번호, 전체 Bold 16pt
    """
    p = doc.add_paragraph()
    run = p.add_run(f'{number}. {title}')
    set_font(run, FONTS['section_title'])
    set_line_spacing(p, 1.3)
    return p

def add_section_subtitle(doc, title):
    """섹션 중제목: 13pt Bold"""
    p = doc.add_paragraph()
    run = p.add_run(title)
    set_font(run, FONTS['section_subtitle'])
    set_line_spacing(p, 1.3)
    return p

def add_body_block(doc, sidebar_text, body_parts):
    """
    SMIC 핵심 레이아웃: 좌측 사이드노트 + 우측 본문.
    
    Args:
        doc: Document 객체
        sidebar_text: 좌측 키워드 (str)
        body_parts: 우측 본문 [(text, is_bold, is_underline), ...]
                    is_bold=True면 Bold 도입문 (첫 문장)
                    is_underline=True면 밑줄 (결론문)
    
    Returns:
        table: 생성된 테이블 객체
    """
    content_w = PAGE.content_width_mm
    sidebar_w = content_w * SIDEBAR_RATIO
    body_w = content_w * BODY_RATIO
    
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(tbl)
    
    # 좌측 사이드노트
    left_cell = tbl.cell(0, 0)
    set_cell_width(left_cell, sidebar_w)
    set_cell_vertical_align(left_cell, 'top')
    
    p_side = left_cell.paragraphs[0]
    if sidebar_text:
        run = p_side.add_run(sidebar_text)
        set_font(run, FONTS['sidebar'])
    set_line_spacing(p_side, FONTS['sidebar'].line_spacing)
    
    # 우측 본문
    right_cell = tbl.cell(0, 1)
    set_cell_width(right_cell, body_w)
    set_cell_vertical_align(right_cell, 'top')
    
    for i, (text, is_bold, is_underline) in enumerate(body_parts):
        if i == 0:
            p = right_cell.paragraphs[0]
        else:
            p = right_cell.add_paragraph()
        
        run = p.add_run(text)
        font_spec = FONTS['body_bold'] if is_bold else FONTS['body']
        set_font(run, font_spec)
        
        if is_underline:
            run.font.underline = True
        
        set_line_spacing(p, font_spec.line_spacing)
    
    return tbl

def add_dual_charts(doc, left_info, right_info):
    """
    하단 차트 2개 병렬 배치.
    
    Args:
        left_info: {
            'title': '도표 1-1. 차트 제목',
            'unit': '단위: 십억 원',
            'image': 'charts/fig_1_1.png',
            'source': 'DART, CUFA',
        }
        right_info: 동일 구조
    """
    chart_w = Mm(PAGE.content_width_mm * 0.48)
    
    # 3행 2열 테이블: 제목 / 이미지 / 출처
    tbl = doc.add_table(rows=3, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(tbl)
    
    for col, info in enumerate([left_info, right_info]):
        if info is None:
            continue
        
        # Row 0: 제목 + 단위
        p_title = tbl.cell(0, col).paragraphs[0]
        run_t = p_title.add_run(info['title'])
        set_font(run_t, FONTS['chart_title'])
        if 'unit' in info and info['unit']:
            run_u = p_title.add_run(f"\n{info['unit']}")
            set_font(run_u, FONTS['chart_unit'])
        
        # Row 1: 이미지
        p_img = tbl.cell(1, col).paragraphs[0]
        if info.get('image'):
            run_i = p_img.add_run()
            run_i.add_picture(info['image'], width=chart_w)
        
        # Row 2: 출처
        p_src = tbl.cell(2, col).paragraphs[0]
        run_s = p_src.add_run(f"출처: {info['source']}")
        set_font(run_s, FONTS['chart_source'])
    
    return tbl

def add_single_chart(doc, info):
    """단독 차트 (전폭). info 구조는 add_dual_charts와 동일."""
    chart_w = Mm(PAGE.content_width_mm * 0.95)
    
    # 제목
    p_title = doc.add_paragraph()
    run_t = p_title.add_run(info['title'])
    set_font(run_t, FONTS['chart_title'])
    if info.get('unit'):
        run_u = p_title.add_run(f"  {info['unit']}")
        set_font(run_u, FONTS['chart_unit'])
    
    # 이미지
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_i = p_img.add_run()
    run_i.add_picture(info['image'], width=chart_w)
    
    # 출처
    p_src = doc.add_paragraph()
    run_s = p_src.add_run(f"출처: {info['source']}")
    set_font(run_s, FONTS['chart_source'])

# ============================================================
# 재무 테이블
# ============================================================

def add_financial_table(doc, headers, rows, title=None):
    """
    SMIC 스타일 재무 테이블.
    
    Args:
        headers: ['', '2023A', '2024A', '2025E', '2026E', '2027E']
        rows: [
            {'label': '매출액', 'values': [1000, 1200, ...], 'bold': True},
            {'label': 'YoY(%)', 'values': ['20%', '10%', ...], 'italic': True},
            ...
        ]
    """
    if title:
        p = doc.add_paragraph()
        run = p.add_run(title)
        set_font(run, FONTS['chart_title'])
    
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header
    
    tbl = doc.add_table(rows=n_rows, cols=n_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 헤더 행
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(str(h))
        set_font(run, FONTS['table_header'])
        # 배경색
        shading = parse_xml(
            f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" '
            f'w:fill="{TABLE_COLORS["header_bg"]}"/>'
        )
        cell._tc.get_or_add_tcPr().append(shading)
    
    # 데이터 행
    for i, row in enumerate(rows):
        for j, val in enumerate([row['label']] + row['values']):
            cell = tbl.cell(i + 1, j)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            
            run = p.add_run(str(val))
            spec = FONTS['table_data']
            set_font(run, spec)
            
            if row.get('bold'):
                run.font.bold = True
            if row.get('italic'):
                run.font.italic = True
            
            # 음수 색상
            if isinstance(val, (int, float)) and val < 0:
                run.font.color.rgb = RGBColor.from_string(TABLE_COLORS['negative'])
            if isinstance(val, str) and val.startswith('-'):
                run.font.color.rgb = RGBColor.from_string(TABLE_COLORS['negative'])
            
            # 짝수행 배경
            bg = TABLE_COLORS['row_even'] if i % 2 == 0 else TABLE_COLORS['row_odd']
            shading = parse_xml(
                f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{bg}"/>'
            )
            cell._tc.get_or_add_tcPr().append(shading)
    
    # 테두리
    set_table_borders(tbl, TABLE_COLORS['border'])
    
    return tbl

def set_table_borders(table, color):
    """재무 테이블용 가는 테두리"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = parse_xml(f'<w:tblPr {nsdecls("w")}/>')
        tbl.insert(0, tblPr)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="2" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="2" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="2" w:space="0" w:color="{color}"/>'
        '</w:tblBorders>'
    )
    # 기존 borders 제거 후 추가
    existing = tblPr.findall(qn('w:tblBorders'))
    for e in existing:
        tblPr.remove(e)
    tblPr.append(borders)

# ============================================================
# 페이지 브레이크
# ============================================================

def add_page_break(doc):
    """새 페이지"""
    from docx.oxml.ns import qn
    p = doc.add_paragraph()
    run = p.add_run()
    br = parse_xml(f'<w:br {nsdecls("w")} w:type="page"/>')
    run._r.append(br)
```

## 5. chart_factory.py — matplotlib 차트 생성

```python
"""
CUFA 표준 차트 생성기.
모든 차트를 라이트 + 다크 2벌 생성.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.dates import DateFormatter
import numpy as np
from config import CHART_LIGHT, CHART_DARK

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

def _setup(theme_dict, figsize=(6, 4)):
    """공통 차트 설정"""
    t = theme_dict
    fig, ax = plt.subplots(figsize=figsize, facecolor=t['bg'])
    ax.set_facecolor(t['bg'])
    ax.tick_params(colors=t['text'], labelsize=8)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    for s in ['left', 'bottom']:
        ax.spines[s].set_color(t['spine'])
        ax.spines[s].set_linewidth(0.5)
    ax.grid(True, color=t['grid'], linewidth=0.5, alpha=0.7)
    ax.xaxis.label.set_color(t['text'])
    ax.yaxis.label.set_color(t['text'])
    ax.title.set_color(t['text'])
    return fig, ax, t

def _save(fig, path, dpi=250):
    fig.tight_layout(pad=1.5)
    fig.savefig(path, dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)

def _add_source(ax, text, t):
    ax.annotate(f'출처: {text}', xy=(0, -0.13), xycoords='axes fraction',
                fontsize=7, color=t.get('gray', '#999999'), ha='left')

def create_chart_both(name, draw_func, *args, **kwargs):
    """
    라이트+다크 2벌 동시 생성.
    draw_func(fig, ax, t, *args, **kwargs)를 호출.
    """
    for theme_name, theme_dict, folder in [
        ('light', CHART_LIGHT, 'charts'),
        ('dark', CHART_DARK, 'charts_dark'),
    ]:
        fig, ax, t = _setup(theme_dict, figsize=kwargs.get('figsize', (6, 4)))
        draw_func(fig, ax, t, *args, **kwargs)
        _save(fig, f'{folder}/{name}.png')

# === 예시 차트 함수들 ===

def draw_price_12m(fig, ax, t, dates, prices, current_price, change_pct, **kw):
    """표지용 12M 주가 차트"""
    ax.plot(dates, prices, color=t['primary'], linewidth=1.5)
    ax.fill_between(dates, prices, alpha=0.1, color=t['primary'])
    ax.set_title('')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    # 현재가 표시
    ax.annotate(f'₩{current_price:,} ({change_pct:+.1f}%)',
                xy=(dates[-1], prices[-1]),
                fontsize=9, color=t['primary'], fontweight='bold',
                ha='right')
    _add_source(ax, 'pykrx, CUFA', t)

def draw_revenue_opm(fig, ax, t, years, revenue, opm, **kw):
    """매출액 + OPM 이중축 차트"""
    ax2 = ax.twinx()
    ax.bar(years, revenue, color=t['primary'], alpha=0.7, width=0.6, label='매출액')
    ax2.plot(years, opm, color=t['negative'], marker='o', markersize=4, label='OPM(%)')
    ax.set_ylabel('매출액 (십억 원)', fontsize=8, color=t['text'])
    ax2.set_ylabel('OPM (%)', fontsize=8, color=t['text'])
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(t['spine'])
    ax2.tick_params(colors=t['text'], labelsize=8)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.1f}%'))
    _add_source(ax, 'DART, CUFA', t)

def draw_pbr_band(fig, ax, t, dates, prices, bps_series, multiples, **kw):
    """Historical PBR 밴드"""
    colors = [t['gray'], t['tertiary'], t['secondary'], t['primary'], t['negative']]
    for i, m in enumerate(multiples):
        band = [bps * m for bps in bps_series]
        ax.plot(dates, band, color=colors[i % len(colors)],
                linewidth=0.8, linestyle='--', alpha=0.6)
        ax.annotate(f'{m:.1f}x', xy=(dates[-1], band[-1]),
                    fontsize=7, color=colors[i % len(colors)])
    ax.plot(dates, prices, color=t['primary'], linewidth=1.5, label='주가')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    _add_source(ax, 'pykrx, DART, CUFA', t)
```

## 6. HTML 디자인 금지 사항 (반드시 준수)

- 귀여운 느낌 절대 금지
- box-shadow 과용 금지
- 과한 글로우/그라데이션 금지
- 모바일앱식 과장 애니메이션 금지
- 데이터 밀도를 떨어뜨리는 여백 남용 금지
- border-radius 최대 4px (둥글둥글 금지)
- 외부 CDN/라이브러리 일체 금지 (순수 HTML/CSS/JS만)

## 7. 찬희님 선호 (최우선 준수)

- **목업 데이터 절대 금지** — API에서 못 가져온 데이터는 빈칸으로
- **시그니처 퍼플**: #7c6af7 (메인) ~ #a78bfa (밝은)
- **다크 배경**: #0a0a0a base / #0f0f0f surface
- **SMIC 레이아웃 100% 복제**: 좌측 사이드노트 + 우측 본문 + 하단 차트 2개 병렬
- **모든 페이지 꽉 차게** — 여백 남용 = 실패
- **단정적 서술체**: "~이다" (○)
- **Bold 도입문 + 밑줄 결론문** 패턴 엄수
- **한국어 100%**
- **불필요한 영어 번역 금지**: 한국어 단어 뒤에 괄호로 영어 번역을 붙이지 말 것. "면(noodle block)", "바이럴(Viral Marketing)", "커모디티(Commodity)" 등 한국어로 충분히 통용되는 단어는 영어 삭제. 금융 전문 약어(OPM, PER, WACC 등)와 고유명사(Walmart, TikTok 등)만 영어 허용. 판단 기준: "이 영어 없이도 한국어 독자가 100% 이해하는가?" → Yes면 영어 제거.

## 8. 89점+ 자동 달성 빌드 시스템 (v8 아키텍처)

### 8-0. 핵심 원칙: Markdown-First 워크플로우

**현대건설 v1의 교훈**: Python에서 직접 HTML을 쓰면 텍스트가 항상 부족해진다.
**해결**: 마크다운으로 먼저 75,000자+ 본문을 작성 → 검증 → HTML 변환.

```
Phase 0: Nexus MCP 데이터 수집 (기본) or 재무데이터 Excel
  → dart_financial_statements: IS/BS/CF 5개년 (CFS 연결 필수!)
  → stocks_market_overview / pykrx: 주가, PER/PBR 밴드
  → ecos_search: 금리, 환율, GDP 등 매크로 변수
  → MCP 실패 시 pykrx/yfinance 직접 호출, 그래도 안 되면 찬희님 수동
  → {종목명}_재무데이터.xlsx 있으면 읽어서 Appendix 자동 생성
  ↓
Phase 1: 마크다운 본문 작성 (75,000자+ 목표)
  → {종목명}_CUFA_본문.md (순수 텍스트+테이블)
  → 섹션별 최소 자수 검증
  ↓
Phase 2: HTML 변환 (build_template.py 기반)
  → 마크다운 본문을 sidebar_wrap()에 삽입
  → SVG 차트/다이어그램 추가
  → 인터랙티브 요소(expand_card, counter_arg, scenario_tabs) 삽입
  → 스크롤 UX(progress, float-toc, dots, page-break) 적용
  ↓
Phase 3: Evaluator 검증 (자동)
  → 89점 체크리스트 전항목 검증
  → 미달 시 자동 보강 → 재검증
  ↓
Output: {종목명}_CUFA_보고서.html (250KB+, 75K자+, SVG 28+, 테이블 25+)
```

### 8-0a. 마크다운 본문 작성 가이드 (Phase 1)

**"SMIC S-Oil 보고서 하나만으로 아무것도 모르는 사람도 이해할 수 있다"**
이것이 우리가 지향하는 수준이다. 모든 보고서는 다음을 충족해야 한다:

#### 섹션별 마크다운 최소 요구사항

```
## 1. 기업개요 (8,000자+)
- 이 기업이 뭘 하는 회사인지 3문장 요약
- 이 산업이 뭔지 비전공자도 이해할 수 있는 기초 설명 (2,000자+)
  - 산업의 구조, 수익 모델, 핵심 용어 정의
  - 밸류체인 각 단계 설명 (원재료→생산→유통→서비스)
- 사업부별 상세 (사업부당 800자+)
  - 매출 비중, 주요 제품/서비스, 경쟁사, 핵심 KPI
- 역사·연혁 (500자+): 설립→성장→현재 핵심 이벤트
- CEO·경영진: 전략 방향, 취임 이후 변화
- 지배구조·주주 구성
- 핵심 경쟁력 3가지 (각 200자+)

## 2. 산업분석 (8,000자+)
- 산업 기초: 시장 규모, 성장률, 구조, 수요 동인 (3,000자+)
  - "이 산업을 처음 접하는 사람도 이해할 수 있도록"
  - 수요-공급 구조, 가격 결정 메커니즘, 진입 장벽
- 사이클 분석: 현재 위치, 과거 사이클 비교 (1,000자+)
- 지역별 시장: 주요 지역 3~5개 각 500자+
- 경쟁 구도: TOP 10 기업, 점유율, 포지셔닝 (1,000자+)
- 메가트렌드: 전동화/디지털화/ESG 등 (500자+)

## 3. IP① (5,000자+)
- 테제 선언 (Bold 1문장)
- 근거 3~5개 (각 600자+, 데이터와 논리로 뒷받침)
- Bear case 선제 논파 (counter_arg): "시장의 우려 → 반박" (500자+)
- 결론 (밑줄)
- 관련 차트 2~3개의 전후 해설

## 4. IP② (5,000자+)
- (3번과 동일 구조)

## 5. IP③ (4,000자+)
- (3번과 동일 구조)
- 밸류에이션 매력이 IP인 경우: 과거 사이클 Analogy 테이블 포함

## 6. 재무분석 (6,000자+)
- 듀폰 분해: NPM × AT × EM = ROE (각 요소 연도별 변동 원인)
- 현금흐름: OCF/CAPEX/FCF 추이 + 변동 원인 서술
- 운전자본: DIO/DSO/DPO 또는 산업 특화 지표 (수주잔고/매출인식 등)
- 재무 안정성: 부채비율, ICR, 유동비율
- 배당 정책: 과거 DPS, 배당성향, 향후 전망
- ROIC vs WACC: 가치 창출/파괴 분석

## 7. Peer 비교 (4,000자+)
- Peer 선정 근거 (왜 이 5개사를 비교하는지)
- 멀티플 비교: PER/PBR/EV-EBITDA/OPM/ROE (각 1문장 해석)
- 차별점 vs 약점 (3개씩)
- 벤치마킹: 1등 기업의 전략에서 배울 점

## 8. 실적추정 (6,000자+)
- P×Q 사업부별 (or 수주전환율/공사진행률 기반)
  - 각 사업부 ASP/Q 추정 근거 400자+
  - 또는 프로젝트별 매출인식 타이밍
- 원가 분해: 7항목+ (자재/인건비/감가/외주/전기광열/R&D/기타)
  - 각 항목 YoY 변동 근거
- 분기별 추정표 + 해설
- Bull/Base/Bear 시나리오 (각 200자+)

## 9. 밸류에이션 (5,000자+)
- WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
- 방법론 3개 (PER + PBR or EV/EBITDA + DCF)
  - 각 방법론의 선택 근거, Target 배수 근거
- Football Field
- DCF 민감도
- 확률 가중 목표주가
- 도달 경로 (2~3단계)

## 10. 리스크 (4,000자+)
- 리스크 5~6개 (각 300자+)
- EPS 민감도 정량화 (변수별 ±영향)
- 최악 시나리오 합산 → Bear Case 검증
- 모니터링 체크포인트 5개
- 리스크 대비 업사이드 비교

## 11. Appendix (3,000자+ 해설 + 테이블 10개+)
- A-1~A-10 필수: IS/BS/CF/주당/Valuation/DCF민감도/Peer/체크리스트/WACC/P×Q확장
- 각 테이블 전에 1~2줄 해설
```

**합계: 58,000자+ (마크다운 본문만). HTML 변환 시 차트 해설·callout·expand 추가로 75,000자+ 달성.**

### 8-0b. "아무것도 모르는 사람도 이해하게" 쓰는 법

SMIC S-Oil 보고서가 89점인 핵심 이유: **정유업을 모르는 사람도 읽고 투자 판단을 내릴 수 있다.**

적용 규칙:
1. **전문용어 첫 등장 시 반드시 정의**: "OPM(영업이익률, Operating Profit Margin)"
2. **비유로 설명**: "수주잔고는 식당의 예약 대기줄과 같다. 길수록 향후 매출이 보장된다"
3. **숫자에 맥락 부여**: "매출 22.1조원"이 아니라 "매출 22.1조원으로 대한민국 GDP의 약 1%에 해당"
4. **"그래서 투자자에게 뭐가 중요한가"로 귀결**: 모든 분석 문단의 마지막 문장은 투자 판단과 연결
5. **산업 기초 2,000자+ 필수**: 섹션1과 섹션2에서 산업의 구조·수익 모델·핵심 용어를 먼저 설명

### 8-1. 아키텍처 (v8)

```
Phase 1 산출물: {종목명}_CUFA_본문.md (마크다운, 75K자+)
Phase 2 산출물: build_{종목명}.py (Python, 헬퍼 재사용)
Phase 3 산출물: {종목명}_CUFA_보고서.html (인터랙티브 HTML, 250KB+)
```

단일 파일 내 구조:
1. **글로벌 도표 카운터** (`_fig_counter`, `fig_num(sec)`)
2. **SVG 헬퍼 함수** (11종 — 아래 참조)
3. **`table()` 헬퍼** — 도표 번호 + 출처 지원
4. **`gen_css()`** — 다크테마 CSS 전체
5. **`gen_cover()`** — 커버 (IS 7열: 2022A~2028E)
6. **`gen_toc()`** — 앵커 링크 TOC (페이지번호 X)
7. **`section_header(num, title)`** — "Equity Research Report | 종목명" 서브헤더 + id
8. **`sidebar_wrap(kws, content)`** — 2열 레이아웃 래퍼
9. **`gen_section1()` ~ `gen_section11()`** — 11개 섹션
10. **`gen_footer()`** + **`build()`** — 조립 + 검증

### 8-2. SVG 헬퍼 함수 16종

**기존 12종 (v4)**

| 함수명 | 용도 | 핵심 파라미터 |
|--------|------|---------------|
| `svg_bar()` | 수직 막대 | labels, values, colors, show_line, sec, unit |
| `svg_line()` | 라인 차트 | labels, datasets[(name,vals,color)], sec, unit |
| `svg_donut()` | 도넛 차트 | segments[(label,val,color)], sec |
| `svg_hbar()` | 수평 막대 | labels, values, sec |
| `svg_waterfall()` | 워터폴 | items[(label,val,type)], sec |
| `svg_scatter()` | 산점도 | points[(name,x,y,color,size)], sec |
| `svg_football()` | 풋볼 필드 | rows[(method,low,high,color)], current, sec |
| `svg_heatmap()` | 히트맵 | row_labels, col_labels, 2D data, sec |
| `svg_grouped_bar()` | 그룹 막대 | labels, group_names, group_data, sec |
| `svg_bubble_risk()` | 리스크 매트릭스 | risks[(name,prob,impact,color,sz)], sec |
| `svg_per_band()` | PER 밴드 | years, prices, per_levels, sec |
| `svg_flow_diagram()` | 플로우 다이어그램 | stages[(label,sublabel,color)], sec |

**신규 4종 (v5)**

| 함수명 | 용도 | 핵심 파라미터 | 벤치마크 출처 |
|--------|------|---------------|-------------|
| `svg_radar()` | 레이더/스파이더 차트 | axes, datasets[(name,vals_0to1,color)] | Peer 다각 비교 |
| `svg_area()` | 누적 면적 차트 | labels, datasets[(name,vals,color)] | 매출 구성 추이 |
| `svg_timeline()` | 수평 타임라인 | events[(date,desc,color)] | YIG 키움 (자사주 소각 스케줄) |
| `svg_comparison_matrix()` | 비교 매트릭스 | row_labels, col_labels, 2D data, colors | SMIC 알지노믹스 (경쟁약물 비교) |
| `svg_annotated_price()` | 이벤트 주석 주가 차트 | dates, prices, events[(date,label,color)], sec | YIG 키움증권 (6개 이벤트 매핑) |
| `svg_tam_sam_som()` | TAM/SAM/SOM 동심원/퍼널 | levels[(label,value,color)], sec | SMIC 로보티즈 (액츄에이터 시장) |

모든 함수 공통:
- `sec` 파라미터 → 자동 "도표 X-Y." 프리픽스
- `style="width:100%;max-width:700px;"` 반응형 (도넛/레이더는 500px)
- Y축 그리드라인(점선) + **Y축 라벨(값)** 기본 포함
- `unit` 파라미터 → "(단위: 억원)" 자동 표시
- `add_source(chart_html, src)` 함수로 출처 추가
  - **주의**: `rfind('</div>')` 사용 — 마지막 `</div>` (chart-box 닫기) 앞에 삽입
- **hover 효과**: CSS `transition + filter:brightness(1.2)` 자동 적용 (rect/circle)

### 8-2b. v5 CSS 컴포넌트

| 클래스 | 용도 | 사용 예시 |
|--------|------|----------|
| `.callout` | 핵심 메시지 강조 박스 (보라 좌측 바) | 섹션 결론, 목표주가 선언 |
| `.insight-box` | 인사이트/시사점 박스 (초록 테두리) | 차트 해석 후 시사점 |
| `.progress-bar > .fill` | 프로그레스 바 | 시너지 실현률, 목표 달성률 |
| `.table-scroll` | 넓은 테이블 스크롤 래퍼 | Appendix 7열+ 테이블 |
| `.section-divider` | 섹션 간 구분선 | 대섹션 전환 |
| `tabular-nums` | 테이블 숫자 정렬 | 자동 적용 (td:not(:first-child)) |

**반응형**: `@media (max-width:768px)` — cover/sidebar/chart-pair/metric-grid 자동 1열 전환
**인쇄**: `@media print` — 배경 흰색, page-break-inside:avoid, A4 마진 2cm

### 8-3. 표준 섹션 구조 (11개)

```
섹션  | 제목                          | 핵심 내용
------|-------------------------------|------------------------------------------
1     | 기업 개요                      | 산업 기초, 장비 종류, 역사, 사업부×5 상세, MLA 밸류체인
2     | 산업 분석                      | 시장 구조/동인, 지역별, 경쟁구도, 전동화/자율주행
3     | 투자포인트 ①                   | 핵심 시너지/차별화, DSA 아키텍처 다이어그램
4     | 투자포인트 ②                   | 글로벌 확장, 지역별 경쟁환경 상세
5     | 투자포인트 ③                   | 밸류에이션 매력, Re-rating 트리거, MSCI
6     | 재무 분석                      | 듀폰 분해, 운전자본(DIO/DSO/DPO), 분기마진, ROIC vs WACC
7     | Peer 비교                      | OPM vs PER 산점도, 벤치마킹
8     | 실적 추정 (P×Q)               | 사업부별 ASP×Q, 분기별 추정, Bull/Base/Bear
9     | 밸류에이션                      | WACC 산출 상세, PER/EV-EBITDA/DCF, Football Field
10    | 리스크 분석                     | EPS 민감도 정량화, 리스크 매트릭스, 모니터링 체크포인트
11    | Appendix                       | A-1~A-14 (IS/BS/CF/주당/Valuation/DCF/Peer/FCFF/체크리스트/확장IS/확장BS/확장CF/P×Q확장/WACC상세)
```

### 8-4. 각 섹션 코드 패턴

```python
def gen_sectionN():
    h = section_header(N, "섹션 제목")
    kws = [("키워드1", "값1"), ("키워드2", "값2"), ...]  # 4~6개
    txt = """
    <p><strong>Bold 도입문으로 핵심 주장 선언.</strong> 보통체로 근거 전개...</p>
    <p>추가 분석 단락...</p>
    <p><strong><u>핵심 결론은 볼드+밑줄로 강조.</u></strong></p>
"""
    h += sidebar_wrap(kws, txt)
    # 차트/테이블은 sidebar_wrap 밖에 배치
    h += '<div class="chart-pair">\n'
    h += add_source(svg_bar("제목", labels, values, sec=N, unit="억원"))
    h += add_source(svg_donut("제목", segments, sec=N))
    h += '</div>\n'
    h += table(headers, rows, highlight_rows={...}, sec=N, title="테이블 제목", src="출처")
    h += '</div>\n'
    return h
```

### 8-5. 검증 기준

| 항목 | 목표 | 비고 |
|------|------|------|
| 텍스트 | 60,000~80,000자 | 컴팩트 but 실질적. 무의미한 반복 금지 |
| SVG 차트 | 25+ | 각 섹션 2~4개 |
| 테이블 | 30+ | 특히 Appendix에 집중 |
| 도표 번호 | 전수 | "도표 X-Y." 형식 |
| 출처 | 전수 | 모든 차트/테이블 하단 |
| sidebar | 전 섹션 | 4~6개 키워드+수치 |
| 파일 크기 | 200KB+ | — |

### 8-6. 종목 교체 시 수정 포인트

새 종목으로 보고서를 만들 때 수정해야 할 부분:
1. `gen_cover()` — 종목명, 투자포인트 3개, IS 데이터, 사이드바 메트릭스
2. `gen_toc()` — 섹션 제목 조정 (투자포인트 내용에 따라)
3. `gen_section1()` — 기업 개요, 사업부 구조, 역사
4. `gen_section2()` — 해당 산업 분석 (산업별 완전 재작성)
5. `gen_section3~5()` — 투자포인트 (종목별 완전 재작성)
6. `gen_section6()` — 재무 데이터 교체 (DART 기반)
7. `gen_section7()` — Peer 그룹 교체
8. `gen_section8()` — P×Q 매출추정 (사업부 구조에 따라)
9. `gen_section9()` — WACC 파라미터, 밸류에이션 수치
10. `gen_section10()` — 종목별 리스크 요인
11. `gen_section11()` — 재무 데이터 교체

헬퍼 함수(svg_*, table, CSS, section_header, sidebar_wrap)는 **재사용** — 수정 불필요.

### 8-7. 서술 원칙 (SMIC 스타일)

- **산업 기초부터 설명**: 장비 종류, 시장 구조, 가격 결정 구조, 유통 구조, 수명 주기 등
  - 처음 보는 사람도 산업을 이해할 수 있어야 함
  - 일반 리서치 보고서(전문가용)와 차별화되는 핵심
- **P×Q 방식 매출추정**: 사업부별 ASP × 수량 = 매출, 각 추정 근거 400자+
- **WACC 산출 과정 명시**: Rf, β, ERP, Ke, Kd, D/E 각 파라미터 선정 근거
- **리스크 정량화**: 각 리스크의 EPS 영향도(원) 산출
- **Bold 도입문 → 보통체 근거 → 밑줄 결론** 패턴 일관 적용
- **불필요한 반복·지엽적 내용·비문 금지** — 컴팩트하되 실질적
- **P×Q 5개년(2024A~2028E)**: Appendix A-13에 사업부별 ASP/Q를 5개년 전체로 제시
- **분량보다 밀도**: 자수 목표에 집착하지 말 것. 의미 있는 분석만 추가

### 8-8. 중복 방지 규칙

같은 데이터를 여러 형식(차트+테이블+도넛)으로 반복하지 말 것.

| 데이터 | 본문 시각화 | Appendix | 금지 |
|--------|------------|----------|------|
| 사업부 매출 비중 | 도넛 1개 | — | 바+도넛+테이블 3중 |
| 지역별 매출 | 바 차트(성장률 오버레이) | 테이블 | 도넛 추가 |
| EPS 추이 | 바 차트 1개 | A-4 주당지표 테이블 | 동일 차트 반복 |
| Peer PER | 산점도(OPM vs PER) | A-7 Peer 상세 테이블 | hbar 추가 |
| WACC 파라미터 | 섹션9 산출 테이블 | A-14 민감도 테이블 | 동일 테이블 복제 |
| P×Q | 섹션8 단년(2026E) | A-13 5개년 확장 | 동일 연도 데이터 반복 |

원칙: **본문은 핵심 1~2개 시각화, Appendix는 상세 테이블로 차별화.**

### 8-9. MLA/DSA 다이어그램 구현 패턴

두 다이어그램은 `svg_flow_diagram()` 헬퍼가 아닌 **인라인 SVG로 직접 구현**한다.

**MLA (밸류체인 계층도, 섹션1):**
- viewBox="0 0 700 420", 5-Layer 수직 구조
- Layer 1(원자재)→2(생산)→3(브랜드)→4(유통)→5(서비스/AM)
- 각 레이어: 가로 600px rect, 세로 간격 85px, ↑ 화살표 연결
- 레이어별 색상: 원자재(#FF4D4D), 생산(#7C6AF7), 브랜드(#A78BFA), 유통(#00E09E), AM(#FFB84D)
- 레이어 안에 핵심 텍스트 + 수치(시너지 금액 등)

**DSA (시너지 시스템 아키텍처, 섹션3):**
- viewBox="0 0 700 280"
- 좌측: 4개 입력 박스(구매통합/CAPEX/R&D/매출시너지)
- 중앙: 합산 박스(시너지 3,000억원)
- 우측: 결과 체인(OPM → EPS → 목표주가) 3단계
- 입력→합산: 수렴 라인, 합산→결과: → 화살표 연결
- **MLA 순서**: 반드시 Layer 1(원자재)이 맨 위, Layer 5(서비스)가 맨 아래. 화살표는 ↓ 방향.

### 8-10. cufa-diagram 스킬 연동

고품질 PNG 다이어그램이 필요할 때 `cufa-diagram` 스킬을 사용한다.
경로: `~/.claude/skills/user/cufa-diagram/`

- SVG 템플릿 6종(MLA, DSA, Cover, Peer, Football Field, Risk Matrix) 제공
- 9색 컬러 팔레트 + 다크 테마 CSS (`widget_base.css`)
- `python svg_to_png.py input.svg output.png` → Playwright 브라우저 렌더링으로 Retina 2x PNG
- 최초 1회: `npx playwright install chromium && npx playwright install-deps chromium`
- HTML 인라인 SVG(build_v4.py)와 별개로, docx/pptx 삽입용 PNG가 필요할 때 사용

## 9. 벤치마크 기반 필수 품질 기준 (14개 보고서 종합 분석)

2026.03.27 기준 4개 대학 투자학회 보고서 14건을 정밀 분석하여 도출한 품질 기준.
분석 원본: `~/Desktop/학회보고서_종합분석.txt`

### 9-0. 벤치마크 보고서 총람

| 학회 | 보고서 수 | 유형 | 평균 페이지 | 평균 글자수 | 평균 도표 | 레벨(60점) |
|------|-----------|------|-------------|-------------|----------|-----------|
| **SMIC** (서울대) | 9건 | 기업분석 | 35.9 | **88,151** | ~46 | **58** |
| **YIG** (연세대) | 2건 | 기업분석 | 30.0 | ~47,000 | ~70 | 39 |
| **S.T.A.R** (성균관대) | 2건 | 산업+기업 | 35.0 | 60,649 | ~67 | 37 |
| **EIA** (이화여대) | 1건 | 기업분석 | 34.0 | 47,656 | N/A | 31 |

SMIC 개별 보고서:

| 종목 | 페이지 | 글자수 | 도표 | Valuation | 차별점 |
|------|--------|--------|------|-----------|--------|
| 알지노믹스 | 35 | 84,334 | 82 | SOTP(rNPV) | 바이오 파이프라인 확률가중 |
| 파마리서치 | 39 | 92,769 | 56+ | Historical PER | 의사 인터뷰 9명, 168건 크롤링 |
| Sensient | 34 | 77,710 | 78 | Historical PER | 미국 주별 규제 매핑 |
| 두산 | 37 | 79,455 | 50 | SOTP(EV/EBITDA) | 지주사 Appx 19개 |
| 코오롱티슈진 | 36 | 96,831 | 36 | DCF | Bull/Bear 확률가중 |
| 풍산 | 33 | 78,892 | 35 | SOTP+PER | 포탄 물량 추정 |
| 로보티즈 | 37 | **121,420** | 35 | DCF(3-scenario) | 10년 추정, Implied PER |
| 애니플러스 | 33 | 75,872 | 34 | Hist. Peer PER | 회귀분석(R²=0.94), OSMU |
| 파마리서치v2 | 39 | 92,769 | 38 | Historical PER | (상동) |

### 9-1. 반드시 포함해야 할 구성 요소

| 요소 | 설명 | 벤치마크 출처 |
|------|------|-------------|
| **매출원가 Bottom-up 분해** | 원가율 퉁치기 금지. 원재료/인건비/감가상각/외주가공/전기광열비 등 항목별 개별 추정 | SMIC S-Oil |
| **반론 선제 논파** | Bear case를 리스크 섹션에 나열하지 말고, 해당 IP 본문에서 먼저 꺼내서 논파 ("시장이 우려하는 점은 ~이다. 그러나 ~" 패턴) | SMIC S-Oil |
| **사이드 캡션 (sidebar)** | 키워드+수치 뿐 아니라 해당 문단의 핵심 메시지 1줄을 우측에 배치. 스캔 리딩 가능하게 | SMIC 전체 |
| **과거 사이클 Analogy 테이블** | 현재와 유사한 과거 시점을 선정, 유사점/차이점을 표로 정리하여 밸류에이션 근거로 활용 | SMIC S-Oil (2015 vs 2026) |
| **Key Chart 인트로 페이지** | TOC 직후에 핵심 차트 4개를 1페이지에 모아 보고서 전체 메시지를 즉각 전달 | YIG 키움증권 |
| **용어 정리 섹션** | 비전문 독자 배려. 산업 특화 용어 10~15개를 표로 정의 | YIG 심텍/키움 |
| **P×Q 제품 세분화** | 사업부 단위가 아니라 제품 단위까지 ASP/Q 분리. 가능하면 고객사/지역별로도 분해 | YIG 심텍 (9개 제품군) |
| **수주/계약 기반 매출 인식** | 수주 기반 기업의 경우 계약건별 계약기간/분기별 매출 인식 타이밍까지 추정 | EIA 인텔리안테크 |
| **비용 추정 섹션 독립** | 매출추정과 별도로 비용추정(원가/판관비) 섹션을 분리하여 투명성 확보 | YIG 심텍/키움 |
| **이중 밸류에이션 크로스체크** | 최소 2개 방법론(PER+DCF, PBR+RIM 등)으로 교차 검증. 결과 수렴 시 신뢰도 급상승 | YIG 전체, EIA |
| **Valuation "Why X? Why not Y?"** | 선택 방법론의 근거 3문장 + 배제 방법론별 부적합 사유 1문장. SMIC 9건 전부 포함하는 핵심 패턴 | SMIC 전체 (로보티즈: "Historical 부적합—지속적자, Peer 부적합—유사기업 부재") |
| **Implied PER sanity check** | DCF 사용 시 터미널연도의 내재 PER을 산출하여 목표주가 합리성 검증. >40x = red flag | SMIC 로보티즈 (Implied PER 25.39x@30E, 9.37x@34E) |
| **지분 희석 반영** | 유상증자/CB전환/RCPS 전환 등에 따른 주식수 변동을 목표주가에 반영. 시나리오 2개 제시 권장 | SMIC 로보티즈 (유상증자), 애니플러스 (CB 콜옵션 행사/미행사 2시나리오) |

### 9-2. 논리 전개 패턴 (벤치마크 공통)

```
[산업분석] 매크로 → 산업 구조 → 경쟁 환경 → 수요/공급 동인
   ↓
[기업분석] 기업 개요 → 사업부 구조 → 기술적 해자 → 주가 이벤트 분석
   ↓
[투자포인트] IP마다: 테제 선언 → 근거 3~5개 → Bear case 선제 논파 → 결론
   ↓
[매출추정] P×Q Bottom-up (제품/고객/지역 세분화) → 분기별 인식
   ↓
[비용추정] 원가 항목별 분해 (원재료/인건비/감가상각/외주 등)
   ↓
[밸류에이션] 2개 방법론 + 민감도 + Football Field
   ↓
[리스크] 정량화(EPS 민감도) + 모니터링 지표
   ↓
[Appendix] IS/BS/CF 5개년 + P×Q 확장 + WACC + Peer + 체크리스트
```

### 9-3. 차별화된 기법 (선택 적용)

| 기법 | 설명 | 적용 상황 |
|------|------|----------|
| **독자적 분석 프레임** | 종목별 고유 개념 도입 (키움: "키움 Multiplier", HD건설기계: "시너지 실현률") | 항상 시도 |
| **Pre 투자포인트** | 본격 IP 전에 "왜 이 회사/산업인가"를 analogie로 선제 논증 | 시장 인지도 낮은 종목 |
| **ASP-변수 회귀분석** | ASP와 핵심 변수(유가, 환율 등)의 회귀식으로 ASP 추정 근거 강화 (R² 제시) | 원자재 가격 연동 기업 |
| **가동률-스프레드 시차 분석** | 과거 데이터에서 선행/후행 관계 발견하여 전망에 활용 | 시클리컬 기업 |
| **ROE-PBR 경로분석** | 과거 복수 구간의 ROE-PBR 회귀선 기울기 비교로 Target Multiple 보수성 검증 | PBR 밸류에이션 시 |
| **산업 패러다임 전환 프레임** | "Phase 1→Phase 2" 같은 거시 프레임으로 독자 관심 유도 | 산업보고서 |
| **회귀분석 매출 모델** | 외부 드라이버와 매출 간 R² 상관관계 기반 추정 (R²>0.85 시 적용). scatter+regression line SVG로 시각화, 회귀식 공개 | SMIC 애니플러스 (일본 신작 애니 수→콘텐츠 매출, R²=0.94) |
| **과거 시점 Peer (Historical Peer)** | 현재 Peer가 아닌 과거 유사 상황의 동일/유사 기업을 비교 대상으로 선정 | SMIC 애니플러스 (대원미디어 2H22를 현재 Peer 대신 선정) |
| **자회사별 개별 추정** | 사업부 단위가 아닌 연결 자회사 각각의 P×Q를 개별 추정 후 합산 | SMIC 애니플러스 (7개 자회사 개별 추정) |
| **OSMU 승수효과 정량화** | IP/콘텐츠 기업의 파생수익을 산업별 벤치마크 배수로 정량화 (Star Wars 3,200%, 평균 740%) | SMIC 애니플러스 (귀멸의 칼날 OSMU 186억원) |
| **선행지표 상관분석** | BS항목(무형자산, CapEx, 재고)과 미래 매출 간 상관계수로 실적 선행지표 식별 (R²>0.90) | SMIC 애니플러스 (무형자산→매출 R²=0.98) |
| **수요-공급 병목 체인** | 수요량→부품개수→공급량→갭 정량화로 밸류체인 병목 지점 도출 | S.T.A.R 중국 반도체 (AI칩→HBM 쇼티지 분석) |
| **유효이자율별 이자추정** | 이자발생자산/부채 항목별 유효이자율 산출 후 정밀 이자손익 추정 | SMIC 파마리서치 (자산별 weighted rate) |
| **웨이퍼-다이 수율 공식** | 반도체 보고서에서 웨이퍼당 생산 가능 다이 수를 물리 공식으로 직접 산출 | S.T.A.R GaN (r, 다이면적, 수율 기반) |
| **해외 사례 크로스체크** | 해외 유사 정책/사례를 국내 전망에 대입하여 효과 검증 (일본 신NISA→한국 밸류업, 중국 대기금→국내 반도체 투자) | YIG 키움증권, S.T.A.R (대기금 1/2/3기) |
| **수수료/비용 내재화 정량 분석** | 중간 단계 제거(캡티브 브로커, 자체 유통망)로 인한 비용 절감을 건당 단가×물량으로 정량 산출 | YIG 키움증권 (캡티브 브로커 2bp=연 170억 절감) |
| **기술 로드맵 연동** | 주요 고객사/플랫폼의 기술 로드맵(Nvidia Hopper→Blackwell→Rubin 등)과 동사 제품 수요를 직접 연결 | S.T.A.R GaN반도체 |
| **규제/정책 실시간 이슈 반영** | 최신 규제 변화(벌금, 수출 제재, 우회 적발 등)를 보고서에 반영하여 시의성 확보 | S.T.A.R (TSMC 10억달러 벌금, CoAsia 우회 수출) |
| **IP 파생 수익화 모델** | 콘텐츠 IP의 지역별 수익화 모델(GEM, AVOD/SVOD, 토큰 등)을 개별 분석 | SMIC 애니플러스 (라프텔 GEM 모델, 동남아) |
| **작품/IP 패러디 소제목** | 분석 대상 IP의 용어/세계관을 섹션 제목에 차용하여 가독성+재미 ("성장의 호흡 제1의 형 「서사」") | SMIC 애니플러스 |

### 9-4. 89점 자동 달성 요건 (5개 영역 × 필수 조건)

**각 영역 18점 이상 = 총점 90점.** 아래 조건을 모두 충족해야 한다.

#### [논리 18점] 필수 조건
- counter_arg 3건+ (IP마다 1건, "시장의 우려 → 반박" 패턴)
- 독자적 분석 프레임 1개 (종목마다 고유한 분석 개념)
- 과거 사이클 Analogy 테이블 (유사 시점과 비교)
- 인과관계 3단+ 체인 (A→B→C→투자결론)
- Bear case를 IP 본문에서 선제 논파 (리스크 섹션이 아니라 IP에서!)
- 1차 데이터 1건+ (전문가 인터뷰/플랫폼 크롤링/커뮤니티 추적/공공데이터 중 택1)

#### [추정 18점] 필수 조건
- P×Q (또는 산업 특화 Bottom-up) 5개년, 사업부별 ASP/Q 각 추정 근거 400자+
- ASP 분해 테이블 (기초→MIX→가격→환율→최종) or 수주전환율 분해
- 원가 7항목+ Bottom-up (자재/인건비/감가/외주/전기광열/R&D/기타)
- 분기별 추정표 + 해설
- 3중 밸류에이션 (PER+PBR or EV/EBITDA+DCF) 크로스체크
- WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
- Football Field + DCF 민감도 히트맵
- "Why X? Why not Y?" 밸류에이션 방법론 선택/배제 근거 섹션 필수
- Implied PER sanity check (DCF 사용 시 터미널연도 내재 PER 합리성 검증)

#### [시각화 18점] 필수 조건
- SVG 28개+ (섹션당 최소 2개)
- MLA 밸류체인 5-Layer SVG (산업 밸류체인)
- DSA 시스템 아키텍처 SVG (핵심 논리 플로우)
- 산업 사이클 포지션 SVG (현재 위치 표시)
- 인터랙티브: expand_card 5+, sticky, progress, float-toc, page-break
- 반응형 3-breakpoint (1024/768/480px)
- hover 효과, tabular-nums

#### [서술력 18점] 필수 조건
- **마크다운 본문 75,000자+ (Phase 1에서 확보)**
- 산업 기초 설명 2,000자+ (비전공자도 이해 가능)
- 전문용어 첫 등장 시 정의
- 모든 차트/테이블 전후에 해설 문단 (pre: "왜 보는가", post: "핵심 시사점")
- 숫자에 맥락 부여 ("22.1조원 = GDP의 ~1%")
- 모든 분석 문단이 "그래서 투자자는"으로 귀결

#### [구조 18점] 필수 조건
- 11섹션 완비 (Appendix 테이블 10개+)
- Key Chart 인트로 + 용어정리 12개+
- 도표번호 전수 + 출처 전수
- callout(KEY TAKEAWAY) 3개+ + insight-box 1개+
- 스크롤 UX 5종 (progress/toc/dots/back-top/page-break)
- 재무데이터 Excel 연동 (있는 경우 자동 Appendix)
- 용어 정리(Glossary) 테이블 10개+ 구현 (gen_glossary 헬퍼)
- Key Chart 인트로 2×2 그리드 구현 (gen_key_charts 헬퍼)

### 9-4b. HARD MINIMUM (이 기준 미달 시 빌드 실패 처리)

**현대건설 v1에서 발견된 문제**: 텍스트 33,205자(목표의 42%), 테이블 9개(목표의 25%), 섹션당 1,200자(목표 4,000자의 30%). 스킬 템플릿을 써도 **내용을 충분히 채우지 않으면** 빈약한 보고서가 나온다.

#### 정량 최소 기준 (빌드 함수에서 자동 검증)

| 항목 | 최소 기준 | 검증 방법 |
|------|----------|----------|
| **총 텍스트** | **50,000자 이상** | `len(text_only) >= 50000` |
| **섹션당 텍스트** | **3,000자 이상** (Appendix 제외) | 섹션별 측정 |
| SVG 차트 | 25개 이상 | `html.count('<svg ') >= 25` |
| 테이블 | 20개 이상 | `html.count('<table') >= 20` |
| 도표 번호 | 40개 이상 | — |
| 출처 | 40개 이상 | — |
| counter_arg | 3건 이상 (IP마다 1건) | `html.count('시장의 우려') >= 3` |
| Appendix 테이블 | 8개 이상 (IS/BS/CF/주당/Valuation/Peer/DCF/체크리스트) | — |

#### 섹션별 필수 구성 요소 (하나라도 빠지면 불완전)

```
[섹션1 기업개요] 최소 4,000자
□ 사업부별 매출 비중 도넛
□ 수주잔고/매출 추이 바 차트
□ MLA 밸류체인 5-Layer SVG
□ expand_card 3개+ (산업 기초, 사업부 상세, 역사)
□ 사업부 비교 테이블
□ KEY TAKEAWAY callout

[섹션2 산업분석] 최소 4,000자
□ 사이클 포지션 SVG
□ 시장 규모 추이 바 차트
□ 지역별/분야별 도넛
□ TOP 10 기업 테이블
□ 차트 전후 해설 문단

[섹션3 IP①] 최소 3,000자
□ counter_arg 1건
□ DSA 시스템 아키텍처 SVG
□ 워터폴 or 타임라인 차트
□ KEY TAKEAWAY callout

[섹션4 IP②] 최소 3,000자
□ counter_arg 1건
□ 지역/분야별 시각 다이어그램
□ 관련 데이터 차트 2개

[섹션5 IP③] 최소 3,000자
□ counter_arg 1건
□ PER 밴드 차트
□ PBR 밴드 차트
□ insight-box

[섹션6 재무분석] 최소 4,000자
□ 매출/OPM 이중축 차트
□ 마진율 추이 라인
□ 현금흐름 그룹 바 or 테이블
□ 듀폰분해 테이블
□ DIO/DSO/DPO 테이블 (건설업이면 수주잔고/매출인식 테이블)
□ ROIC vs WACC 테이블
□ 재무 요약 테이블

[섹션7 Peer비교] 최소 2,500자
□ OPM vs PER 산점도
□ 레이더 차트
□ Peer 비교 테이블

[섹션8 실적추정] 최소 4,000자
□ P×Q 사업부별 매출 추정 테이블
□ 분기별 추정 테이블
□ ASP 분해 테이블 (or 수주전환율 분해)
□ 매출원가 Bottom-up 분해 테이블
□ EPS 추이 바 차트
□ Bull/Base/Bear 시나리오
□ 연간 실적 추정 요약 테이블

[섹션9 밸류에이션] 최소 3,000자
□ WACC 산출 상세 테이블
□ Football Field SVG
□ DCF 민감도 히트맵
□ 밸류에이션 Summary 테이블
□ 워터폴 (확률 가중 목표주가)

[섹션10 리스크] 최소 3,000자
□ EPS 민감도 테이블
□ 리스크 매트릭스 버블 SVG
□ 모니터링 체크포인트 테이블
□ EPS 영향도 시각화 SVG

[섹션11 Appendix] 최소 5,000자
□ A-1: 포괄손익계산서 (7열: 2022A~2028E)
□ A-2: 재무상태표
□ A-3: 현금흐름표
□ A-4: 주당지표
□ A-5: 밸류에이션 Summary
□ A-6: DCF 민감도 매트릭스
□ A-7: Peer 상세 비교
□ A-8: 투자 체크리스트
```

#### 빌드 함수 자동 검증 코드

```python
# build() 함수 마지막에 반드시 포함
HARD_MIN = {
    'text_50k': (text_chars >= 50000, f'text {text_chars:,} < 50,000'),
    'svg_25': (svg_count >= 25, f'SVG {svg_count} < 25'),
    'tables_20': (table_count >= 20, f'tables {table_count} < 20'),
    'counter_arg_3': (html.count('시장의 우려') >= 3, 'counter_arg < 3'),
    'appendix_8': (html.count('A-') >= 8, 'Appendix tables < 8'),
    'glossary_10': (glossary_count >= 10, 'glossary terms < 10'),
    'why_not_val': ('부적합' in html or 'Why not' in html, 'valuation exclusion rationale missing'),
}
fails = [msg for ok, msg in HARD_MIN.values() if not ok]
if fails:
    print('\\n!!! HARD MINIMUM FAILURES !!!')
    for f in fails:
        print(f'  FAIL: {f}')
    print('보고서 품질 미달 — 내용을 보강할 것.')
```

### 9-5. HTML 보고서 전체 체크리스트

빌드 후 반드시 확인:

```
[구조]
□ 커버: 투자의견/목표주가/IS 7열+/Key Metrics/Bull-Base-Bear
□ TOC: 앵커링크 (페이지번호 X)
□ Key Chart 인트로: 핵심 차트 4개 모아 1페이지
□ 용어 정리: 산업 특화 용어 10~15개 테이블
□ 전 섹션 sidebar-layout + 사이드 캡션(키워드+메시지)
□ 섹션 헤더: "Equity Research Report | 종목명 (코드)"

[분석 품질]
□ 산업분석: 시장 구조/동인/경쟁/전동화 등 기초부터 설명
□ 투자포인트: IP별 Bear case 선제 논파 포함
□ 과거 사이클 Analogy 테이블 포함
□ 독자적 분석 프레임 1개 이상

[추정 품질]
□ P×Q: 제품 단위까지 세분화, 5개년(2024A~2028E)
□ 매출원가: 항목별 Bottom-up 분해 (원가율 퉁치기 금지)
□ 비용추정: 판관비도 인건비/R&D/기타 분리
□ 분기별 추정표 포함
□ 운전자본: DIO/DSO/DPO/CCC

[밸류에이션]
□ 최소 2개 방법론 크로스체크
□ WACC 산출 상세 (Rf/β/ERP/Ke/Kd 각 파라미터 근거)
□ Football Field 차트
□ DCF 민감도 매트릭스

[리스크]
□ EPS 민감도 정량화 (변수별 ±영향)
□ 리스크 매트릭스 (발생확률 × 영향도)
□ 모니터링 체크포인트 테이블

[시각화]
□ SVG 25개+, 테이블 30개+
□ 도표 번호 전수 ("도표 X-Y.")
□ 출처 전수 (chart-box 하단)
□ MLA 밸류체인 계층도 (Layer 1→5, ↓ 방향)
□ DSA 시너지 아키텍처 (입력→합산→결과)
□ 중복 차트 금지 (동일 데이터 2개 형식 이하)

[Appendix]
□ IS/BS/CF 5개년
□ 주당지표
□ Valuation Summary
□ DCF 민감도
□ Peer 상세
□ FCFF 상세
□ 투자 체크리스트
□ 추정 IS/BS/CF 확장 (통합 기준)
□ P×Q 5개년 확장
□ WACC 민감도
```

## 10. 시각화 고급 기법 (STAR/EIA/웹 리서치 종합)

### 10-1. 차트 내 콜아웃 박스 (STAR GaN 벤치마크)

차트 안에 빨간 테두리 박스나 화살표로 핵심 인사이트를 직접 삽입하는 패턴.
독자가 차트를 해석할 필요 없이 "이걸 봐라"를 명시.

```python
# SVG 차트 내 콜아웃 예시
svg += f'<rect x="..." y="..." width="120" height="30" rx="4" fill="none" stroke="#FF4D4D" stroke-width="1.5" stroke-dasharray="4"/>'
svg += f'<text x="..." y="..." fill="#FF4D4D" font-size="9" text-anchor="middle">핵심 인사이트</text>'
```

### 10-2. 주가 이벤트 주석 차트 (EIA 인텔리안 벤치마크)

주가 라인 차트 위에 주요 이벤트(수주 공시, 실적 발표, 합병 발표 등)를 화살표+텍스트로 직접 표기.
"왜 이 시점에 주가가 움직였는가"를 시각적으로 설명.

### 10-3. Sticky 헤더 (웹 리서치)

HTML 보고서에서 스크롤해도 종목명/목표가/투자의견이 항상 화면 상단에 노출.
```css
.sticky-header { position:sticky; top:0; z-index:100; background:var(--bg);
  padding:8px 20px; border-bottom:1px solid var(--border); }
```

### 10-4. 다크 테마 색상 정밀 규칙 (Material Design + 웹 리서치)

| 레벨 | 용도 | 권장 색상 | 금지 |
|------|------|----------|------|
| 배경 L0 | 전체 배경 | `#0F0F16` (블루 틴트) | 순수 블랙 `#000000` |
| 배경 L1 | 카드/패널 | `#1A1A28` | |
| 배경 L2 | 호버/활성 | `#252538` | |
| 본문 텍스트 | 기본 | `#E0E0E0` | 순수 화이트 `#FFFFFF` |
| 보조 텍스트 | 출처/캡션 | `#9E9E9E` ~ `#B0B0B0` | `#888` 이하 (WCAG 미달) |
| 악센트 | 최대 3색 | 퍼플+틸+앰버 | 6색 초과 |

### 10-5. 금융 테이블 국제 표준 (CFA + 웹 리서치)

- **음수 표기**: 괄호 `(1,234)` + 빨간색 (△ 기호도 OK)
- **세로선 없음**: 가로 구분선만 사용 (금융 보고서 표준)
- **합계/소계 행**: 상단 1px 실선 + 볼드
- **추정치 구분**: 연도에 "E" 접미사 (2026E), 컬럼 배경색 미세 차이
- **`font-variant-numeric: tabular-nums`** 전역 적용

### 10-6. 사이드 마진노트 패턴 (STAR/SMIC/EIA 공통)

모든 벤치마크 보고서의 공통 디자인 요소:
- 좌측 여백(페이지 폭의 ~20%)에 해당 단락의 **핵심 메시지 1줄**을 배치
- 바쁜 독자가 마진노트만 훑어도 전체 논지 파악 가능 (skim reading 최적화)
- HTML에서는 `sidebar-layout`의 `.sidebar-kw`에 키워드+수치 뿐 아니라 **핵심 메시지 문장**도 포함

### 10-7. 차트 디자인 금지 사항 (웹 리서치 종합)

- 3D 효과 절대 금지
- 불필요한 그라디언트/그림자 금지 (chart junk)
- 색상 12개 초과 금지 (6개 이하 권장)
- 순수 빨강-녹색 조합 금지 (색맹 대응 → 청-주황 권장)
- 범례를 차트 밖에 분리하지 말고 데이터 위에 직접 라벨링
- Y축 라벨(값) 누락 금지 — 그리드라인만 있으면 의미 없음

## 11. 전 항목 19점 달성 설계 (v6+ 자동화 패턴)

2026.03 벤치마크 평가(SMIC/YIG/STAR/EIA 6건 vs 우리 v5) 결과:
- 시각화 18점(1위), 구조 18점(공동1위) → 유지
- **논리 14점(꼴찌), 서술력 14점(꼴찌), 추정 16점** → 개선 필수

### 11-1. 논리/분석력 14→19: 반론 선제 논파 자동화

**문제**: Bear case를 리스크 섹션에 나열만 함. IP 본문에서 정면 반박 안 함.
**해결**: 매 투자포인트에 `counter_arg()` 블록 삽입.

```python
def counter_arg(concern, rebuttal):
    """반론 선제 논파 블록 (SMIC S-Oil 벤치마크)"""
    return f'''<div style="background:rgba(255,77,77,0.05);border-left:3px solid var(--red);padding:12px 16px;margin:16px 0;border-radius:0 6px 6px 0;">
<p style="font-size:13px;color:var(--red);font-weight:600;margin-bottom:6px;">시장의 우려</p>
<p style="font-size:13px;color:var(--text-sec);margin-bottom:8px;">{concern}</p>
<p style="font-size:13px;color:var(--green);font-weight:600;margin-bottom:6px;">반박</p>
<p style="font-size:13px;color:var(--text);margin:0;">{rebuttal}</p>
</div>'''
```

**필수 적용 위치** (매 IP에 최소 1개):

| 섹션 | 우려 | 반박 |
|------|------|------|
| IP1 시너지 | "합병 시너지 3,000억원은 과대 추정 아닌가? 과거 건설기계 합병에서 시너지 미달 사례가 많다" | "Komatsu-Joy Global(매출 대비 3.5%), Volvo-Terex(3~4%) 사례에서 동일 수준 실현. HD건설기계 3,000억원은 합산 매출의 3.6%로 업종 평균 범위 내" |
| IP2 업사이클 | "중국 부동산 침체가 장기화되면 글로벌 업사이클 자체가 무산되는 것 아닌가?" | "중국 비중 15%이며, 북미 IIJA+인도 Gati Shakti+중동 NEOM의 정부 주도 인프라 투자는 경기 독립적. 중국 제외 나머지 85% 지역의 성장률만으로도 +5% 달성 가능" |
| IP3 밸류에이션 | "합병 초기 PER 프리미엄이 과도하며, Korea Discount가 해소될 근거가 없다" | "합병 리스크 프리미엄은 시간 감소 특성. PMI 완료(2027)와 함께 자연 해소. MSCI 편입($4.9B > 기준 $3B)으로 패시브 자금 $300~500M 유입 기대" |

**논리 점수 올리는 추가 기법**:
- **독자적 분석 프레임**: 종목마다 1개 이상의 고유 개념 도입 (키움의 "키움 Multiplier"처럼)
  - 예: "시너지 실현률(SRR: Synergy Realization Rate)" — 분기마다 추적 가능한 지표
- **인과관계 체인**: 매 IP에서 "A이므로 B → B이므로 C → C이므로 D(투자결론)" 3단 이상 체인
- **정량적 반박**: "~가 우려되지만, 실제 영향은 EPS 기준 ±X원에 불과하다" 숫자로 반박

### 11-2. 추정/밸류에이션 16→19: ASP 근거 + 원가 분해 심화

**문제**: ASP 추정이 "MIX 개선" 한 줄. 원가 항목이 7개로 얕음.
**해결**: ASP 분해 테이블 + 원가 12항목 분해.

```python
# ASP 분해 테이블 (v6 필수)
table(
    ["ASP 변동 요인", "2025A", "영향(%)", "2026E ASP", "근거"],
    [
        ["기초 ASP", "1.75억", "—", "1.75억", "2025 실적 기준"],
        ["MIX 개선 (대형↑)", "—", "+1.7%", "+0.03억", "대형 비중 18%→20%, ASP 2배"],
        ["가격 인상", "—", "+1.1%", "+0.02억", "원자재 전가 + Tier4F 고사양"],
        ["환율 효과", "—", "+0.0%", "—", "1,350원 가정 (현행 유지)"],
        ["최종 ASP", "1.75억", "+2.9%", "1.80억", ""],
    ],
    highlight_rows={4}
)
```

**원가 12항목 분해 (v6 필수)**:
1. 원재료비 (철강/유압/전장) — 매출원가의 60%
2. 인건비 (생산직) — 15%
3. 감가상각비 — 3.5%
4. 외주가공비 — 8%
5. 전기광열비 — 3%
6. 수선비 — 2%
7. 경상연구개발비 — 2.5%
8. 포장운반비 — 1.5%
9. 보험료 — 0.8%
10. 임차료 — 0.7%
11. 소모품비 — 1.5%
12. 기타 — 1.5%

각 항목에 YoY 변동률 + 변동 근거 1문장 필수.

### 11-3. 서술력 14→19: 차트 전후 해설 자동화

**문제**: 차트가 연속 나열되고 해설 문단이 빠진 구간 다수.
**해결**: `chart_with_context()` 래퍼로 강제 해설 삽입.

```python
def chart_with_context(pre_text, chart_html, post_text):
    """차트 전후 해설 문단 강제 삽입 (SMIC 패턴)"""
    h = f'<p style="font-size:14px;line-height:1.8;color:var(--text);margin-bottom:12px;">{pre_text}</p>\n'
    h += chart_html
    h += f'<p style="font-size:14px;line-height:1.8;color:var(--text);margin:12px 0;">{post_text}</p>\n'
    return h
```

**필수 규칙**:
- `chart_with_context(pre, chart, post)` 없이 `svg_*()` 직접 호출 금지
- 단, `<div class="chart-pair">` 안의 2열 차트는 pair 전후로 1세트만 적용 가능
- pre_text: "이 데이터를 왜 봐야 하는가" (최소 3문장, 200자)
- post_text: "핵심 시사점 + 그래서 투자자는 어떻게" (최소 3문장, 200자)

**서술 밀도 체크 자동화**:
```python
# build 함수 마지막에 자동 검증
sections = html.split('class="section"')
for i, sec in enumerate(sections[1:], 1):
    charts = sec.count('<svg ')
    texts = len(re.findall(r'<p[^>]*>(.{100,}?)</p>', sec))
    if charts > 0 and texts / charts < 2:
        print(f"  WARNING: sec{i} 차트당 해설 문단 {texts/charts:.1f}개 (최소 2개 필요)")
```

### 11-4. 시각화 18→19: 미세 개선

이미 1위지만 19점을 위해:
- **차트 내 콜아웃 박스**: 핵심 데이터 포인트에 빨간 점선 사각형 + 인사이트 텍스트 (STAR GaN 벤치마크)
- **annotated 주가 차트**: 주요 이벤트(합병 발표, 실적 발표)를 주가 선 위에 직접 표기 (EIA 벤치마크)
- **바 차트 width 통일**: 모든 바 차트에서 bar_w를 동일하게 고정

### 11-5. 구조 18→19: 비용추정 독립 섹션

현재 섹션8에 매출추정+비용추정이 통합되어 있음.
v6에서는 섹션을 12개로 확장:
```
1. 기업개요
2. 산업분석
3. IP① 시너지
4. IP② 글로벌 확장
5. IP③ 밸류에이션
6. 재무분석
7. Peer 비교
8. 매출추정 (P×Q)      ← 분리
9. 비용추정 (원가 분해)  ← 분리 (v6 신규)
10. 밸류에이션
11. 리스크
12. Appendix
```

### 11-6. v6 빌드 체크리스트 (전 항목 19점 기준)

```
[논리 19점]
□ 매 IP에 counter_arg() 반론 선제 논파 1개+
□ 독자적 분석 프레임 1개 (SRR, Multiplier 등)
□ 인과관계 3단 체인 (A→B→C→투자결론)
□ 정량적 반박 ("EPS ±X원에 불과")

[추정 19점]
□ ASP 분해 테이블 (기초+MIX+가격+환율=최종)
□ 원가 12항목 Bottom-up (각 항목 YoY 근거)
□ 비용추정 독립 섹션 (판관비도 인건비/R&D/수수료/기타 분리)
□ P×Q 5개년, 분기별 추정표

[시각화 19점]
□ 차트 내 콜아웃 박스 (핵심 데이터에 빨간 점선 사각형)
□ annotated 주가 차트 (이벤트 주석)
□ 바 차트 width 통일
□ 기존 v5 요소 전부 유지

[서술력 19점]
□ 매 차트/테이블에 chart_with_context(pre, chart, post)
□ pre: "왜 보는가" 3문장 200자+
□ post: "핵심 시사점" 3문장 200자+
□ 서술 밀도 자동 검증 (차트당 해설 2문단 이상)

[구조 19점]
□ 12개 섹션 (비용추정 독립)
□ 기존 v5 요소 전부 유지
□ 비용추정 섹션에 원가 12항목 + 판관비 4항목
```

## 12. 스크롤 피로 해소 UX (v7+ 필수)

HTML 보고서가 250KB+로 길어지면 스크롤 피로가 심각. 5가지 UX 요소를 필수 적용.

### 12-1. 읽기 진행률 바
- 최상단 고정(position:fixed), 퍼플 그라데이션, 3px 높이
- `requestAnimationFrame` + `passive:true`로 성능 최적화

### 12-2. Floating Sticky TOC
- 우측 고정(right:16px, top:80px), 반투명 배경, backdrop-filter:blur
- `IntersectionObserver` 또는 scroll handler로 현재 섹션 하이라이트(.active)
- 1200px 미만에서 자동 숨김(@media)

### 12-3. 시각적 페이지 구분선
- 대섹션 전환(기업분석→재무, 추정→밸류에이션, 리스크→Appendix)에 배치
- 그라데이션 수평선 + 중앙에 "FINANCIAL ANALYSIS" 등 영문 라벨
- `.page-break` 클래스, height:60px, margin:48px 0

### 12-4. Back to Top 버튼
- 우하단 고정, 퍼플 원형, scrollY > 400에서 표시
- hover 시 배경색 반전, smooth scroll

### 12-5. 섹션 도트 인디케이터
- 좌측 고정(left:12px), 세로 나열, 현재 섹션 활성화(scale 1.6 + 퍼플)
- 클릭 시 해당 섹션으로 smooth scroll
- 1200px 미만에서 자동 숨김

### 12-6. 성능 규칙
```javascript
// 반드시 requestAnimationFrame + passive 사용
let ticking = false;
window.addEventListener('scroll', () => {
  if(!ticking){
    requestAnimationFrame(() => { updateUI(); ticking = false; });
    ticking = true;
  }
}, {passive:true});
```

## 13. SMIC 수준 자동 생성 메커니즘 (종합)

다음 종목 보고서 빌드 시 자동으로 89점+가 나오는 구조:

### 13-1. 빌드 파이프라인
```
1. build_vN.py 복사 (헬퍼 함수 재사용)
2. 종목별 데이터 교체 (gen_cover ~ gen_section11)
3. 필수 체크:
   □ counter_arg() 3건+ (IP마다 1건)
   □ ASP 분해 테이블 (기초→MIX→가격→환율→최종)
   □ 매출원가 Bottom-up 7항목+
   □ 차트 전후 해설 문단 6건+
   □ Key Chart 인트로 + 용어정리
   □ 과거 사이클 Analogy 테이블
   □ MLA + DSA 다이어그램
   □ 스크롤 UX 5종 (진행률바/TOC/구분선/Back to Top/도트)
4. 빌드 → 자동 검증 → 문제 있으면 수정 후 재빌드
```

### 13-2. 자동 검증 항목 (build 함수에 포함)
```python
# 빌드 후 자동 체크
checks = {
    'counter_arg': html.count('시장의 우려') >= 3,
    'chart_context': len(re.findall(r'margin:12px 0', html)) >= 6,
    'asp_decomp': 'ASP 변동 요인' in html,
    'mla_diagram': '밸류체인 계층도' in html,
    'dsa_diagram': '시스템 아키텍처' in html,
    'key_charts': 'Key Charts' in html,
    'glossary': '용어 정리' in html,
    'cycle_analogy': '과거 사이클' in html,
    'progress_bar': 'reading-progress' in html,
    'float_toc': 'float-toc' in html,
    'page_breaks': 'page-break' in html,
    'text_75k': text_chars >= 75000,
    'svg_25': svg_count >= 25,
    'tables_30': table_count >= 30,
}
for name, passed in checks.items():
    status = 'OK' if passed else 'FAIL'
    print(f'  [{status}] {name}')
```

### 13-3. 우리만의 강점 (절대 포기하지 않을 것)
1. **인터랙티브 HTML** — 정적 PDF 학회 대비 압도적 시각 경험
2. **다크 테마 퍼플** — 브랜드 아이덴티티
3. **hover/sticky/progress** — 읽기 경험 최적화
4. **MLA/DSA 인라인 SVG** — 아키텍처 시각화
5. **16종 SVG 헬퍼** — 어떤 데이터든 즉시 시각화 가능
6. **인터랙티브 요소** — PDF 학회 절대 불가. 클릭/호버/탭 전환

## 13-4. 인터랙티브 요소 (HTML 전용 킬러 피처)

PDF 학회들이 절대 따라올 수 없는 우리만의 무기. 3가지 인터랙티브 헬퍼:

### expand_card(title, meta, content)
클릭하면 펼쳐지는 MLA/DSA 스타일 카드. 긴 상세 정보를 접어두고 필요시 펼침.
- **사용처**: 생산거점 상세, Appendix 재무제표, 사업부 심층 분석
- **효과**: 스크롤 피로 감소 + 정보 계층화
```python
h += expand_card("울산 공장 (본사)", "대형 굴착기·휠로더 | 연 12,000대",
    '<p>상세 설명...</p>')
```

### scenario_tabs(bull, base, bear)
Bull/Base/Bear 시나리오를 탭으로 전환. 3개 시나리오를 같은 공간에 표시.
- **사용처**: 섹션8 실적추정, 섹션9 밸류에이션
```python
h += scenario_tabs(bull_html, base_html, bear_html)
```

### data_tip(text, tip)
마우스 올리면 상세 설명 팝업. 전문 용어나 핵심 수치에 적용.
- **사용처**: 본문 내 전문용어, 핵심 가정 수치
```python
f'WACC {data_tip("10.0%", "Ke 10.1% × 54% + Kd 3.4% × 46% + 합병리스크 3%p")}를 적용'
```

### 인터랙티브 적용 가이드
| 요소 | 위치 | 용도 |
|------|------|------|
| expand_card × 4~6 | 섹션1 생산거점, 섹션11 Appendix | 상세 정보 접기 |
| scenario_tabs × 1 | 섹션8 Bull/Base/Bear | 시나리오 전환 |
| data_tip × 10+ | 전 섹션 핵심 수치 | 가정 근거 표시 |
| hover 효과 | 모든 SVG rect/circle | 데이터 강조 |
| sticky 헤더 | 전체 | 종목/투자의견 상시 노출 |
| progress bar | 전체 | 읽기 진행률 |
| float TOC | 우측 | 현재 섹션 추적 |
| section dots | 좌측 | 빠른 섹션 이동 |

## 14. Builder-Evaluator 패턴 (Anthropic Labs GAN 영감)

Anthropic Labs의 "만드는 Claude + 심사하는 Claude" 패턴을 보고서 빌드에 적용.
단일 에이전트의 한계: (1) 컨텍스트 불안감으로 후반 품질 저하, (2) 자기 작품에 대한 편향.

### 14-1. 3-Agent 파이프라인

```
Phase 1: Planner (에이전트 1)
- 종목 분석 프레임 설계
- IP 3개 + Bear case 3개 사전 구조화
- P×Q 사업부 분류, ASP/Q 추정 방향 설정
- 독자적 분석 프레임 1개 제안

Phase 2: Builder (에이전트 2)
- build_template.py 복사 → 종목별 데이터 교체
- 섹션 1~11 본문 작성
- SVG 차트 + 테이블 생성
- counter_arg 3건+, chart_with_context 적용

Phase 3: Evaluator (에이전트 3) ← 핵심
- 생성된 HTML을 직접 읽고 심사
- 5개 항목(논리/추정/시각화/서술력/구조) × 20점 채점
- "차트당 해설 문단 수" 자동 계산
- counter_arg 존재 여부 확인
- 구체적 개선 지시 → Builder에게 전달
- 85점 이상 될 때까지 반복
```

### 14-2. Evaluator 프롬프트 (서브에이전트용)

```
생성된 HTML 보고서를 읽고 5개 항목을 20점 만점으로 채점하라.
SMIC S-Oil(89점)을 기준으로 극도로 냉정하게 평가.

[논리] counter_arg 3건 이상? 독자적 프레임? 인과 3단 체인?
[추정] ASP 분해 테이블? 원가 7항목+? P×Q 5개년? 분기별?
[시각화] SVG 25+? 도표번호 전수? MLA/DSA? hover/sticky?
[서술력] 차트당 해설 2문단? 공허 문장 0? 실증적 근거?
[구조] 11섹션? Appendix A-1~14? 리스크 독립? Key Chart?

85점 미만이면 구체적 개선 지시를 3줄 이내로 제시.
```

### 14-3. Claude Code 실행 패턴

```python
# 실제 사용 시 (Claude Code에서)
# Phase 1: Plan
plan_agent = Agent(prompt="종목 분석 프레임 설계...")

# Phase 2: Build
build_agent = Agent(prompt="build_template.py 기반 보고서 생성...")

# Phase 3: Evaluate
eval_agent = Agent(prompt="생성된 HTML 심사, 85점 이상까지 반복...")

# Phase 4: Fix (Evaluator 피드백 기반)
fix_agent = Agent(prompt="Evaluator 지적사항 수정...")
```

## 15. 빌드 템플릿 (build_template.py)

`~/.claude/skills/user/cufa-equity-report/build_template.py` (2,403줄)

종목 교체 시 수정 포인트:
1. `gen_cover()` — 종목명, IS 데이터, 사이드바
2. `gen_toc()` — 섹션 제목
3. `gen_key_charts()` — 핵심 수치 4개
4. `gen_glossary()` — 산업 용어
5. `gen_section1~11()` — 본문 전체
6. Sticky bar — 종목명/목표가/투자의견
7. Float TOC — 섹션 목록
8. `build()` output 경로

헬퍼 함수(svg_*, table, counter_arg, add_source, CSS, JS)는 **수정 불필요** — 그대로 재사용.

## 16. 디자인 안티패턴 금지 (바이브코딩 교훈)

AI 생성 보고서가 "AI가 만든 티"가 나지 않도록:

### 16-1. 금지 목록
- Inter 폰트 단독 사용 금지 → Noto Sans KR + 커스텀 페어링
- 뻔한 파란 그라데이션 금지 → 퍼플(#7C6AF7) 시그니처
- 둥근 카드 나열 금지 → 아키텍처형 구조 (MLA/DSA)
- 3D/글로우/네온 효과 금지
- "모던하고 깔끔한" 같은 모호한 지시 금지 → 구체적 레퍼런스 첨부
- Lucide 아이콘 디폴트 금지 → 텍스트 기반 또는 커스텀 SVG

### 16-2. 반드시 할 것
- **디자인 시스템 먼저**: 색상/폰트/간격 규칙을 CSS 변수로 정의 후 빌드 시작
- **레퍼런스 스크린샷**: SMIC S-Oil PDF의 특정 페이지를 레퍼런스로 제공
- **일관성 우선**: 페이지 간 스타일 통일이 독창성보다 중요
- **데이터 밀도**: 여백 남용 = 실패. 모든 공간에 정보를 채울 것

### 16-3. Nexus MCP 데이터 파이프라인 (실데이터 자동 수집)

보고서 작성 시 mock 데이터 대신 Nexus MCP로 실데이터를 자동 수집한다.
131개 도구 중 보고서에 필요한 핵심 도구:

```bash
# MCP 연결 (최초 1회)
claude mcp add nexus-finance --transport http http://62.171.141.206/mcp
```

| 데이터 | MCP 도구 | 사용 예시 |
|--------|---------|----------|
| 재무제표 (IS/BS/CF) | `dart_financial_statements` | "HD건설기계 재무제표 5개년" |
| 주가 데이터 | `stocks_market_overview` | "HD건설기계 주가 추이" |
| Peer 재무 | `dart_financial_statements` | "Caterpillar, Komatsu 재무 비교" |
| 거시경제 | `ecos_search` | "한국은행 기준금리, GDP 성장률" |
| 환율 | `forex_*` | "원/달러 환율 추이" |
| 원자재 | `crypto_*` 또는 외부 | "철강 가격 추이" |
| 산업 통계 | `rone_*` | "건설투자 추이" |

**빌드 파이프라인에 통합:**
```
Phase 0: Data Collection (Nexus MCP)
  → DART 재무제표 → P×Q 기초 데이터
  → pykrx 주가 → PER/PBR 밴드
  → ECOS 매크로 → 산업 분석 배경
Phase 1: Plan → Phase 2: Build → Phase 3: Evaluate
```

찬희님이 MCP를 확장하면 추가 데이터 소스(Bloomberg, 관세청, 산업통상자원부 등)도 자동 수집 가능.
**핵심: mock 데이터 절대 금지 → MCP에서 못 가져온 건 빈칸으로 두고, 찬희님에게 수동 입력 요청.**

- **멀티플 표기 규칙**: PER/PBR/EV-EBITDA에 반드시 기준 시점 명시
  - Forward: `Fwd PER 13.85배` 또는 `PER(12MF)`
  - Trailing: `PER(T) 25.20배`
  - 추정 기반: `2026E PER 14.8배`
  - Target: `Target PER 17.8배`
  - "PER 14배"처럼 기준 없이 쓰는 것 금지
- **산업별 미니멀 SVG 심볼**: `cufa-diagram` 스킬의 심볼 라이브러리 활용
  - 각 종목 보고서마다 해당 산업 심볼 4~6개를 SVG로 제작
  - MLA 다이어그램·섹션 제목·테이블·사이드바에 인라인 삽입
  - "글만 있는 보고서"에서 "보는 보고서"로 전환

## 17. 시스템 기반 보고서 생성 원칙 (X 글쓰기 시스템 + 바이브코딩 교훈)

### 17-1. 80/20 시스템 원칙
- **80%는 시스템이 잡아준다**: 구조, 문체, 포맷, 도표번호, 출처, sidebar, CSS — build_template.py가 자동 처리
- **20%는 사람이 다듬는다**: 투자 논리의 핵심, Bear case 반박의 설득력, 종목 특화 인사이트
- "매번 처음부터 쓰는 게 아니라, 시스템 위에서 쓴다"
- 반복 판단(구조/포맷/키워드)을 시스템에 맡기고, 소재 선택과 최종 다듬기에 집중

### 17-2. 피드백 루프로 시스템 진화
- 보고서 작성할 때마다 불편한 점 → 스킬에 규칙 추가
- "이건 매번 반복하는 지시인데?" → 헬퍼 함수로 자동화
- 예: 차트 해설이 빠짐 → `chart_with_context()` 함수화
- 예: 반론 논파 빠짐 → `counter_arg()` 함수화
- 예: 멀티플 기준 시점 누락 → 표기 규칙 추가

### 17-3. 디자인 시스템 우선 (바이브코딩 핵심)
- **코드 전에 디자인 시스템 정의**: CSS 변수(:root), 색상 팔레트, 폰트, 간격 규칙
- **레퍼런스 스크린샷 제공**: SMIC/YIG 보고서 특정 페이지를 시각적 참고로
- **모방 > 상상**: AI에게 "깔끔하게"라고 말하지 말고, 깔끔한 게 뭔지 보여줄 것
- **일관성 > 독창성**: 페이지 간 스타일 통일이 최우선
- **AI 생성 티 제거**: Inter 폰트 단독 X, Lucide 아이콘 X, 뻔한 파란 그라데이션 X

### 17-4. 재무데이터 Excel → Appendix 자동 생성 파이프라인

**핵심**: 보고서 작성 전에 항상 재무데이터를 엑셀(`.xlsx`)로 정리한다. 이 엑셀을 읽어서 Appendix 테이블을 자동 생성하면 수작업 ZERO.

#### 엑셀 표준 시트 구조
```
{종목명}_재무데이터.xlsx
├── Sheet1: IS (포괄손익계산서) — 매출/원가/GPM/판관비/영업이익/OPM/순이익/EPS (7열: 2022A~2028E)
├── Sheet2: BS (재무상태표) — 유동자산/비유동/총자산/유동부채/비유동/총부채/자기자본/부채비율
├── Sheet3: CF (현금흐름표) — 영업CF/투자CF/재무CF/FCF
├── Sheet4: Per-Share (주당지표) — EPS/BPS/DPS/PER/PBR/배당수익률
├── Sheet5: Peer (피어비교) — 시총/PER/PBR/OPM/ROE/배당/해외비중
├── Sheet6: Valuation — PER방법/PBR방법/DCF/WACC파라미터
└── Sheet7: PxQ (사업부별) — ASP/Q/매출/YoY (5개년)
```

#### 자동 생성 코드 패턴
```python
import openpyxl

def load_financial_data(xlsx_path):
    """엑셀에서 재무데이터를 읽어 dict로 반환"""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    data = {}
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        headers = [cell.value for cell in ws[1]]
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            rows.append(list(row))
        data[sheet_name] = {'headers': headers, 'rows': rows}
    return data

def gen_appendix_from_xlsx(xlsx_path):
    """엑셀 데이터로 Appendix HTML 자동 생성"""
    data = load_financial_data(xlsx_path)
    h = '<div class="appendix">\n'

    sheet_titles = {
        'IS': 'A-1. 포괄손익계산서 (억원)',
        'BS': 'A-2. 재무상태표 (억원)',
        'CF': 'A-3. 현금흐름표 (억원)',
        'Per-Share': 'A-4. 주당지표',
        'Peer': 'A-5. Peer 상세 비교',
        'Valuation': 'A-6. 밸류에이션 Summary',
        'PxQ': 'A-7. P×Q 워크시트',
    }

    for sheet_name, title in sheet_titles.items():
        if sheet_name in data:
            d = data[sheet_name]
            h += f'<p style="font-size:13px;color:var(--text-sec);margin:24px 0 12px;">'
            h += f'<strong style="color:var(--purple-light);">{title}</strong></p>\n'
            h += table(
                [str(x) for x in d['headers']],
                [[str(cell) if cell is not None else '' for cell in row] for row in d['rows']],
                src="DART, CUFA 추정"
            )
    h += '</div>\n'
    return h
```

#### 사용 방법
```python
# build 함수에서
xlsx_path = r"C:\Users\lch68\Desktop\{종목명}_재무데이터.xlsx"
if os.path.exists(xlsx_path):
    h += gen_appendix_from_xlsx(xlsx_path)
else:
    h += gen_section11()  # 수동 Appendix 폴백
```

**워크플로우**: 재무데이터 엑셀 정리(찬희님) → build 스크립트가 자동으로 읽어서 Appendix 생성 → 수작업 ZERO

### 17-5. 디자인 도구 체인
- **Stitch by Google** (stitch.withgoogle.com): 음성 대화로 UI 디자인. 한국어 지원. Figma/Google AI Studio로 export 가능
  - 보고서 레이아웃 프로토타입에 활용 → 스크린샷 찍어서 AI에게 "이 스타일을 따라줘"
  - MCP 지원으로 실시간 배포 가능
- **Excalidraw**: 와이어프레임 스케치 → AI에게 구조 전달
- **Dribbble/Mobbin**: 레퍼런스 스크린샷 수집
- **Google Fonts**: Noto Sans KR + 개성 있는 display 폰트 조합


## 15. 밸류에이션 방법론 확장 (14개 보고서 기반)

### 15-1. 방법론 8종 매트릭스

| 방법론 | 언제 사용 | 언제 부적합 | 벤치마크 |
|--------|----------|------------|---------|
| Historical PER | 안정적 이익, 비교 가능한 과거 존재 | 적자 기업, 사이클 저점 | SMIC 파마리서치, Sensient |
| Historical PBR | 자산 중심, 금융업 | 자산 경량, 고성장 | YIG 심텍, 키움증권 |
| EV/EBITDA | 자본집약, 국가 간 비교 | EBITDA 음수, 규제 산업 | SMIC 두산 (SOTP 내) |
| DCF | 장기 성장, Peer 부재 | 짧은 영업 이력, 변동성 CF | SMIC 로보티즈, 코오롱티슈진 |
| RIM (초과이익모형) | 금융업, 안정적 BPS 성장 | 자본 변동성 큰 기업, 적자 | YIG 키움증권 |
| rNPV | 바이오 파이프라인 기업 | 비제약 기업 | SMIC 알지노믹스 |
| SOTP | 다각화 지주사, 복합 사업 | 단일 사업 | SMIC 두산, 풍산 |
| Historical Peer (과거 시점) | 현재 Peer 부적합, 과거 유사 상황 존재 | 과거 아날로그 없음 | SMIC 애니플러스 |

### 15-2. "Why X? Why not Y?" 템플릿

모든 밸류에이션 섹션에 반드시 포함해야 하는 방법론 선택/배제 근거 블록. SMIC 9건 전부 이 패턴을 따름.

```python
def valuation_rationale(chosen, chosen_reason, excluded_list):
    """밸류에이션 방법론 선택/배제 근거 블록 (SMIC 필수 패턴)

    Args:
        chosen: 선택한 방법론명 (str)
        chosen_reason: 선택 근거 3문장 (str)
        excluded_list: [(방법론명, 부적합 사유), ...] 2개+

    Examples:
        valuation_rationale(
            "DCF",
            "동사의 내재가치를 평가하는 방법으로 절대가치평가법인 DCF를 선택하였다. "
            "Historical 멀티플은 지속된 적자로 적합한 레코드가 부족하며, "
            "현재 시장이 동사에 기대하는 폭발적 성장을 담을 수 있는 유사한 과거 상황이 없다.",
            [
                ("Historical PER", "지속적 적자로 과거 PER 레코드 부적합"),
                ("Peer 멀티플", "상장된 유사 기업 부재, 글로벌 Peer도 사업 구조 상이"),
            ]
        )
    """
    h = '<div style="background:rgba(124,106,247,0.05);border-left:3px solid var(--purple);padding:16px;margin:20px 0;border-radius:0 4px 4px 0;">\n'
    h += f'<p style="color:var(--purple-light);font-size:14px;font-weight:700;margin-bottom:8px;">선택 방법론: {chosen}</p>\n'
    h += f'<p style="color:var(--text);font-size:13px;line-height:1.7;margin-bottom:12px;">{chosen_reason}</p>\n'
    h += '<div style="border-top:1px solid var(--border);padding-top:12px;">\n'
    for method, reason in excluded_list:
        h += f'<p style="color:var(--text-sec);font-size:13px;margin:4px 0;">✕ <strong>{method}</strong> 부적합: {reason}</p>\n'
    h += '</div></div>\n'
    return h
```

### 15-3. Implied PER Sanity Check

DCF로 목표주가를 산출한 경우, 터미널연도의 Implied PER을 역산하여 목표가의 합리성을 검증한다.

```
Implied PER = 목표주가 ÷ 터미널연도 EPS
```

판단 기준:
- Implied PER < 15x (터미널연도): 보수적 — 추가 상승 여력 존재
- Implied PER 15~30x: 합리적 범위
- Implied PER 30~40x: 공격적 — 고성장 전제 필요, 근거 보강
- Implied PER > 40x: Red Flag — 성장 가정 재검토 필수

벤치마크: SMIC 로보티즈 (Implied PER 25.39x@30E, 9.37x@34E → 10년 뒤 합리적)

```python
def implied_per_check(target_price, terminal_eps, terminal_year):
    """Implied PER sanity check (DCF 필수 동반)"""
    implied = target_price / terminal_eps if terminal_eps > 0 else float('inf')
    flag = '합리적' if implied < 30 else ('공격적' if implied < 40 else 'Red Flag')
    return f'''<div style="background:var(--surface2);padding:12px 16px;margin:12px 0;border-radius:4px;">
    <p style="font-size:13px;color:var(--text-sec);">Implied PER Sanity Check ({terminal_year}E)</p>
    <p style="font-size:15px;color:var(--text);font-weight:600;">
      목표주가 {target_price:,.0f}원 ÷ {terminal_year}E EPS {terminal_eps:,.0f}원 = <span style="color:{'var(--green)' if implied < 30 else 'var(--red)'};">{implied:.1f}x</span> ({flag})
    </p></div>'''
```

### 15-4. RIM (초과이익모형) 구현 패턴

YIG 키움증권이 PBR 밸류에이션의 보조 검증으로 사용. 금융업 종목에서 특히 유효.

```
V₀ = BPS₀ + Σ(RI_t / (1+COE)^t) + TV
RI_t = (ROE_t - COE) × BPS_{t-1}
TV = RI_n × (1+g) / (COE - g) / (1+COE)^n
```

파라미터:
- COE (Cost of Equity): CAPM = Rf + β × MRP
  - YIG 키움증권: COE 12.12% (Rf 3.186%, β 1.79, MRP 4.99%)
- TGR (Terminal Growth Rate): 보수적 0% 권장 (YIG 키움증권 사례)

```python
def rim_valuation(bps_0, roe_forecast, coe, tgr, years=5):
    """RIM (Residual Income Model) 밸류에이션
    roe_forecast: [ROE_1, ROE_2, ..., ROE_n] (소수점, e.g., 0.16)
    coe: Cost of Equity (소수점, e.g., 0.12)
    tgr: Terminal Growth Rate (소수점, e.g., 0.0)
    """
    bps = bps_0
    ri_pv_sum = 0
    for t, roe in enumerate(roe_forecast, 1):
        ri = (roe - coe) * bps
        ri_pv = ri / (1 + coe) ** t
        ri_pv_sum += ri
        bps = bps * (1 + roe)  # retained earnings
    # Terminal Value
    ri_n = (roe_forecast[-1] - coe) * bps
    tv = ri_n * (1 + tgr) / (coe - tgr) / (1 + coe) ** len(roe_forecast) if coe > tgr else 0
    intrinsic = bps_0 + ri_pv_sum + tv
    return intrinsic
```

### 15-5. SOTP (Sum of Parts) 구현 패턴

SMIC 두산, 풍산에서 사용. 다각화 지주사/복합기업의 표준 밸류에이션.

```
NAV = Σ(사업부_i × EV/EBITDA_i) + 비영업자산 - IBD
주당 NAV = NAV / 유통주식수
목표주가 = 주당 NAV × (1 - 지주사 할인율)
```

SOTP 테이블 패턴:
```python
table(
    ["사업부", "EBITDA(E)", "적용 배수", "사업가치", "비중", "근거"],
    [
        ["굴착기", "5,200억", "8.5x", "44,200억", "52%", "Caterpillar 8.2x, Komatsu 9.1x 평균"],
        ["엔진", "1,800억", "7.0x", "12,600억", "15%", "Cummins 7.3x 참조"],
        ...
        ["합계", "—", "—", "85,000억", "100%", ""],
        ["(+) 비영업자산", "", "", "2,500억", "", "토지 공정가치"],
        ["(-) IBD", "", "", "12,000억", "", ""],
        ["NAV", "", "", "75,500억", "", ""],
    ],
    highlight_rows={-3, -1}
)
```


## 16. 1차 데이터 수집 가이드 (SMIC 최대 차별점)

SMIC 파마리서치의 독보적 강점 = 1차 데이터 수집. 이를 체계화하여 매 보고서에 최소 1건 포함.

### 16-1. 전문가 인터뷰 프로토콜

**사전 준비**:
- 질문 5개 이상 구조화 (투자포인트 검증용)
- 정량적 답변을 유도하는 질문 설계 ("연간 몇 건?", "비중이 몇 %?")
- 인터뷰이의 전문 분야와 경력 확인

**인터뷰 진행**:
- 녹취 동의 확보 → 전문(transcript) Appendix 수록
- 핵심 인용문은 본문 IP에서 직접 인용 ("현직 의사 A씨에 따르면...")

**Appendix 포맷**:
```python
expand_card(
    "전문가 인터뷰 #1 — 피부과 전문의 (경력 12년)",
    "인터뷰일: 2026.03.15 | 소속: 서울 강남구 소재 피부과",
    """<p><strong>Q1. 리쥬란 시술 수요 변화는?</strong></p>
    <p>A1. "23년 대비 25년 시술 건수가 약 30% 증가했다. 특히 중국인 환자 비중이..."</p>
    ..."""
)
```

벤치마크: SMIC 파마리서치 — 현직 피부과 의사/의료인력 9명 직접 인터뷰 전문 수록

### 16-2. 플랫폼 데이터 크롤링

| 플랫폼 | 데이터 유형 | 활용 예시 | 출처 표기법 |
|--------|------------|----------|-----------|
| 강남언니 | 시술 가격 | ASP 역산 (중위값/평균) | "강남언니 N건 시술가격 크롤링 기준 (2026.03)" |
| 네이버 쇼핑 | 제품 가격·판매량 | 국내 소비자 가격 추이 | "네이버 쇼핑 검색 기준" |
| Amazon | 리뷰 수·가격 | 해외 시장 침투도 | "Amazon.com 제품 리뷰 N건 기준" |
| App Store/Play Store | 앱 순위·리뷰 | 플랫폼 성장세 | "App Annie / Sensor Tower" |
| Kobis | 영화 관객수 | IP 매출 추정 | "영화진흥위원회 통합전산망" |

핵심 원칙: **크롤링 데이터는 반드시 수집 건수·일자·방법론을 명시.** "168건 크롤링"처럼 정량적으로.

### 16-3. 커뮤니티/소셜 시그널 추적

| 시그널 | 추적 방법 | 활용 | 벤치마크 |
|--------|----------|------|---------|
| 카페 게시글 수 | 월별 게시글 카운트 → 수요 선행지표 | 내국인 소비 트렌드 | SMIC 파마리서치 (여우야 카페) |
| TikTok 조회수 | 제품/브랜드 관련 영상 조회수 추적 | 바이럴 마케팅 효과 검증 | SMIC 파마리서치 (크리스 제너 360만 조회) |
| Google Trends | 키워드 검색 지수 월별 추적 | 소비자 관심도 proxy | 범용 |
| Amazon 리뷰 수 | 제품 리뷰 누적 추이 | 해외 시장 침투 속도 | SMIC 파마리서치 |
| AGF/행사 참석인원 | 연도별 참석인원 | 서브컬처 시장 성장 | SMIC 애니플러스 (AGF 72,081명) |

### 16-4. 공공데이터 활용

| 데이터 소스 | 종류 | 활용 예시 |
|------------|------|----------|
| 건강보험심사평가원 | 가입자/상실자, 진료 건수 | 의사 인력 변동, 시술 건수 추정 |
| 관세청 수출입통계 | 품목별 수출입액 | 수출 기업 매출 검증 |
| 한국은행 ECOS | 금리, 환율, GDP | 매크로 변수 |
| 산업통상자원부 | 생산/출하/재고 | 제조업 경기 판단 |
| 영화진흥위원회 Kobis | 일별 관객수/매출 | 콘텐츠 기업 IP 수익 추정 |
| 전력거래소 | 전력 소비량 | 데이터센터/제조업 가동률 proxy |

### 16-5. 1차 데이터 Appendix 포맷

```
Appx N. [데이터 유형] (수집일: YYYY.MM.DD)

수집 방법: [크롤링/인터뷰/공공데이터 다운로드]
수집 건수: [N건/N명/N개월]
수집 범위: [기간, 지역, 플랫폼]
원시 데이터: [테이블로 전수 제시]

출처: [플랫폼명], CUFA [팀명]
```


## 17. 고급 매출추정 기법 (14개 벤치마크 종합)

기본 P×Q를 넘어서는 고급 추정 기법. 종목 특성에 따라 선택 적용.

### 17-1. 회귀분석 기반 매출 모델

외부 드라이버와 매출 간 통계적 관계가 강할 때 (R² > 0.85) 적용.

**필수 산출물**:
1. 산점도 + 회귀선 SVG (`svg_scatter()` + 회귀선 overlay)
2. 회귀식: `Y = aX + b` (계수, 절편 명시)
3. R² 값 명시 (결정계수)
4. 추정 근거 서술: "일본 현지 신작 수(X)와 동사 콘텐츠 매출(Y) 간 R²=0.94의 강한 양의 상관"

벤치마크: SMIC 애니플러스 (일본 신작 애니 수 → 콘텐츠 매출, R²=0.94)

### 17-2. 자회사별 개별 추정

연결 자회사가 5개 이상이고 각각의 사업 특성이 다른 경우, 사업부 단위가 아닌 자회사 단위로 P×Q.

```
연결 매출 = Σ(자회사_i 매출) - 내부거래 제거
```

테이블 패턴:
```python
table(
    ["자회사", "P (ASP)", "Q", "매출", "YoY", "추정 근거"],
    [
        ["본사 콘텐츠", "—", "—", "150억", "+12%", "일본 신작수 회귀(R²=0.94)"],
        ["라프텔", "4,900원/월", "45만명", "265억", "+28%", "AVOD→SVOD 전환 14만명"],
        ["애니맥스", "—", "—", "80억", "+35%", "귀멸 IP 방영권"],
        ...
        ["합계", "", "", "850억", "+22%", "내부거래 제거 후"],
    ],
    highlight_rows={-1}
)
```

벤치마크: SMIC 애니플러스 (7개 자회사 개별 추정)

### 17-3. 선행지표 식별 및 활용

BS 항목(무형자산, CapEx, 재고자산)과 미래 매출 간 시차 상관분석.

**절차**:
1. BS 항목과 1~4분기 래깅된 매출 간 상관계수 산출
2. R² > 0.90인 관계 발견 시 선행지표로 공식 채택
3. dual-axis 차트로 시각화 (좌: 선행지표, 우: 매출, 시차 표시)
4. 해당 선행지표의 최근 값으로 향후 매출 preview

벤치마크: SMIC 애니플러스 (무형자산 투자액 → 1분기 후 콘텐츠 매출, R²=0.9825)

### 17-4. OSMU / 승수효과 정량화

IP/콘텐츠 기업에서 원작 매출 대비 파생 수익(굿즈, 게임, 라이선싱 등)의 배수.

| IP 사례 | 원작 매출 | 파생 매출 | OSMU 배수 |
|---------|----------|----------|----------|
| Star Wars | 영화 $10.3B | 굿즈/게임 $42B | 3,200% |
| Lion King | 영화 $1.7B | 뮤지컬/굿즈 $8.1B | 490% |
| Toy Story | 영화 $3.1B | 굿즈/테마파크 $16B | 530% |
| **평균** | | | **740%** |

적용 예: "귀멸의 칼날 무한성 극장 수익 22억원 × OSMU 배수 740% → 파생 수익 ~163억원 → 보수적 조정 186억원"

벤치마크: SMIC 애니플러스


## 18. 독자적 분석 프레임 템플릿

매 보고서에 1개 이상의 종목/산업 고유 분석 도구를 개발하여 차별화.

### 18-1. 명명 규칙

`"[기업/산업명] [지표명]"` 형식. 측정 가능하고, 시간에 따라 추적 가능하며, 이 분석에서만 사용되는 고유 개념.

### 18-2. `proprietary_metric()` 헬퍼

```python
def proprietary_metric(name, formula, description, tracking, viz_html=""):
    """독자적 분석 프레임 블록

    Args:
        name: 지표명 (e.g., "키움 Multiplier")
        formula: 산식 (e.g., "K% / G% (키움 수수료 수익 성장률 / 시장 거래대금 성장률)")
        description: 지표 의미 설명 2~3문장
        tracking: 추적 방법 (e.g., "분기별 공시 기반 산출, 과거 5년 평균 109.2%")
        viz_html: 시각화 HTML (차트 등, 선택)
    """
    h = f'''<div style="background:var(--purple-bg);border:1px solid var(--purple-border);padding:20px;margin:20px 0;border-radius:4px;">
    <p style="color:var(--purple-light);font-size:16px;font-weight:700;margin-bottom:8px;">{name}</p>
    <p style="color:var(--text);font-size:13px;margin:4px 0;"><strong>산식:</strong> {formula}</p>
    <p style="color:var(--text);font-size:13px;line-height:1.7;margin:8px 0;">{description}</p>
    <p style="color:var(--text-sec);font-size:12px;"><strong>추적:</strong> {tracking}</p>
    {viz_html}
    </div>'''
    return h
```

### 18-3. 사례 아카이브

| 지표명 | 산식 | 기업/산업 | 출처 |
|--------|------|----------|------|
| 키움 Multiplier | K%/G% (키움 수수료 성장률 / 시장 거래대금 성장률) | 키움증권 | YIG 3조 |
| 시너지 실현률(SRR) | 실현 시너지 / 발표 시너지 × 100 (분기별 추적) | HD건설기계 | CUFA (자체) |
| OSMU 배수 | 파생수익 / 원작수익 × 100 | 콘텐츠 기업 | SMIC 애니플러스 |
| 리쥬란 침투율 | 리쥬란 시술건수 / 전체 피부시술건수 | 파마리서치 | SMIC 2팀 |
| HBM 쇼티지율 | (수요 스택수 - 공급 스택수) / 수요 스택수 × 100 | 반도체 장비 | S.T.A.R |


## 19. 용어 정리 (Glossary) 구현 상세

### 19-1. 배치 위치

TOC 직후, Key Chart 인트로와 동일 페이지 또는 바로 직후. `id="glossary"`로 TOC에서 링크.

### 19-2. `gen_glossary()` 헬퍼

```python
def gen_glossary(terms):
    """용어 정리 테이블 (YIG 키움증권 벤치마크)

    Args:
        terms: [(용어, 정의, 영문), ...] 10~15개

    Example:
        gen_glossary([
            ("OPM", "영업이익을 매출액으로 나눈 비율. 본업의 수익성 지표", "Operating Profit Margin"),
            ("WACC", "기업의 자금 조달 비용의 가중 평균. DCF 할인율로 사용", "Weighted Average Cost of Capital"),
            ("P×Q", "가격(Price)×수량(Quantity) 방식의 매출 추정법", "Price × Quantity"),
            ...
        ])
    """
    h = '<div id="glossary" style="margin:32px 0;">\n'
    h += '<h3 style="font-size:18px;color:var(--purple-light);margin-bottom:16px;">용어 정리</h3>\n'
    h += table(
        ["용어", "정의", "영문"],
        [[t, d, e] for t, d, e in terms],
        sec=0, title="산업 핵심 용어", src="CUFA 정리"
    )
    h += '</div>\n'
    return h
```

### 19-3. 최소 요구사항

- **최소 10개, 권장 15개**
- 섹션1~2에서 처음 등장하는 산업 특화 용어 전부 포함
- 밸류에이션 용어 (PER, PBR, EV/EBITDA, WACC, DCF, FCFF, beta 등)도 비전공자 배려하여 포함
- 금융업이면 종투사/발행어음/NCR 등 업종 특화 용어 필수 (YIG 키움증권 사례)


## 20. Key Chart 인트로 구현 상세

### 20-1. `gen_key_charts()` 헬퍼

```python
def gen_key_charts(charts_4):
    """Key Chart 인트로 페이지 (YIG 키움증권 벤치마크)
    TOC 직후 배치. 보고서 전체 메시지를 차트 4개로 즉각 전달.

    Args:
        charts_4: [(svg_html, caption), ...] 정확히 4개
        caption: 1줄 핵심 메시지 (e.g., "매출 CAGR +15%, OPM 구조적 개선")
    """
    h = '<div id="key-charts" style="margin:40px 0;">\n'
    h += '<h3 style="font-size:18px;color:var(--purple-light);margin-bottom:24px;text-align:center;">Key Charts</h3>\n'
    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">\n'
    for svg, caption in charts_4:
        h += f'<div style="text-align:center;">\n{svg}\n'
        h += f'<p style="font-size:12px;color:var(--text-sec);margin-top:8px;line-height:1.4;">{caption}</p>\n</div>\n'
    h += '</div></div>\n'
    return h
```

### 20-2. 차트 선택 가이드

보고서 유형에 따른 4개 차트 선택:

| 위치 | 기업분석 보고서 | 산업 보고서 |
|------|---------------|-----------|
| 좌상 | 매출/OPM 추이 (핵심 실적) | 시장 규모 추이 |
| 우상 | 목표주가 도달 경로 (현재가→목표가) | TAM/SAM/SOM |
| 좌하 | 핵심 IP 관련 차트 (시너지/파이프라인/점유율) | 경쟁 구도 |
| 우하 | Peer 비교 산점도 (OPM vs PER) | 밸류체인 |


## 21. 산업보고서 모드

S.T.A.R(성균관대)의 GaN 반도체/중국 반도체 굴기 보고서 분석 결과, 산업+기업 복합 보고서의 차별화된 구조 확인.

### 21-1. Part 기반 구조

기업분석 보고서의 11섹션과 달리 Part 구조 사용:

```
Part 1: 산업 개요 + 기술 기초 (소재 물성, 공정, 밸류체인)
Part 2: 수요 동인 (시장별/용도별 세분화)
Part 3: 공급 구조 + 경쟁 환경
Part 4: 밸류체인 + 투자 전략 (병목 지점 → 수혜 기업)
Part 5: 기업분석 (개별 종목 1~3개, 간략 투자포인트)
```

### 21-2. 기업분석 모드와 차이점

| 항목 | 기업분석 보고서 | 산업보고서 |
|------|---------------|-----------|
| 구조 | 11섹션 (번호) | 5 Part (테마) |
| Valuation | 필수 (목표주가 산출) | N/R 또는 간단 상대가치 |
| P×Q 매출추정 | 필수 (사업부별) | 없음 (TAM/SAM/SOM 대체) |
| Appendix | IS/BS/CF 필수 | 없음 또는 간략 |
| 도표 넘버링 | "도표 X-Y" | "도표 N" (순번) |
| 핵심 차트 유형 | 실적 추정, PER Band | 시장 규모, 점유율, 기술 비교 |
| 목표 분량 | 75,000자+ | 50,000자+ |
| 캐치프레이즈 | 종목 테마 | 산업 테마 ("GaN다 GaN다 뿅 GaN다!") |

### 21-3. 트리거 분기

```python
# 사용자 요청에 따라 분기
if "산업보고서" in request or "산업분석" in request or "thematic" in request:
    # Part 기반 구조, Valuation 없음, TAM/SAM/SOM 중심
    mode = "industry"
else:
    # 기본: 11섹션 기업분석 보고서
    mode = "equity"
```

### 21-4. 산업보고서 필수 요소 (S.T.A.R 벤치마크)

- 기술 깊이: 소재 물성/공정 수준까지 설명 (GaN: 밴드갭, HEMT, 에피택셜)
- 수요-공급 정량 분석: 수요량 → 부품 개수 → 공급량 → 갭 산출 (병목 체인)
- 주요 플레이어 비교표: TOP 10 기업 × 5~6개 지표
- 정책/규제 매핑: 국가별 규제 현황 테이블
- 투자 전략 명시: "어떤 밸류체인 포지션에 투자해야 하는가" 결론
