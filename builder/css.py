"""CUFA Builder — 단일 표준 CSS 생성기.

HD건설기계 v4-1 CSS 기반. 절대 수정 금지. 새 테마가 필요하면
`design_tokens.py` 의 변수를 바꾸거나, 여기에 추가 셀렉터만 append.

디자인 토큰:
- border-radius 2px (고정)
- 폰트: Noto Sans KR (Google Fonts @import)
- 다크 기본 + 라이트 `[data-theme="light"]` 오버라이드
"""
from __future__ import annotations


def gen_css() -> str:
    """완성된 CSS 문자열을 반환. `<style>{gen_css()}</style>` 로 사용."""
    return _CSS


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
/* 기본: 다크 테마 */
:root, [data-theme="dark"] {
  --bg: #0a0a0a; --surface: #111111; --surface2: #1a1a1a;
  --border: #2a2a2a; --border2: #3a3a3a;
  --purple: #7c6af7; --purple-light: #a78bfa; --purple-bg: #12101f; --purple-border: #2d2654;
  --text: #e0e0e0; --text-sec: #888888; --text-tert: #555555;
  --positive: #4ecdc4; --negative: #ff6b6b; --blue: #6cb4ee; --amber: #ffd93d;
  --font: 'Noto Sans KR', sans-serif;
  --border-radius: 2px;
}
/* 화이트 테마 */
[data-theme="light"] {
  --bg: #ffffff; --surface: #f8f8f8; --surface2: #f0f0f0;
  --border: #e0e0e0; --border2: #cccccc;
  --purple: #7c6af7; --purple-light: #6355d8; --purple-bg: #f3f0ff; --purple-border: #d4ccff;
  --text: #333333; --text-sec: #666666; --text-tert: #999999;
  --positive: #0d9488; --negative: #dc2626; --blue: #2563eb; --amber: #d97706;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--text); font-family:var(--font); font-size:12px; line-height:1.5; }
.report { max-width:960px; margin:0 auto; padding:20px; }
h1 { font-size:24px; font-weight:800; }
h2 { font-size:16px; font-weight:700; }
h3 { font-size:13px; font-weight:600; }
.section { margin-bottom:24px; }
.sticky-header { position:sticky; top:0; z-index:100; background:rgba(var(--bg-rgb,255,255,255),0.95); backdrop-filter:blur(8px); padding:6px 20px; border-bottom:1px solid var(--border); color:var(--text); display:flex; justify-content:space-between; align-items:center; font-size:11px; }
[data-theme="dark"] .sticky-header { background:rgba(10,10,10,0.92); }
[data-theme="light"] .sticky-header { background:rgba(255,255,255,0.95); }
.theme-toggle { cursor:pointer; padding:2px 8px; border:1px solid var(--border); border-radius:12px; font-size:10px; color:var(--text-sec); background:var(--surface); margin-left:12px; }
.section-subheader { font-size:10px; color:var(--text-sec); text-align:right; padding:4px 0; border-bottom:1px solid var(--border); margin-bottom:16px; }
.section-header { display:flex; align-items:center; gap:12px; margin-bottom:24px; padding-bottom:8px; border-bottom:2px solid var(--purple); }
.section-num { background:var(--purple); color:#fff; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:14px; flex-shrink:0; }
.section-title { font-size:22px; font-weight:700; }
.sidebar-layout { display:grid; grid-template-columns:160px 1fr; gap:16px; margin-bottom:20px; }
.sidebar-kw { border-right:2px solid var(--purple); padding-right:12px; }
.sidebar-kw .kw { font-size:11px; font-weight:700; color:var(--purple); margin-bottom:4px; }
.sidebar-kw .kw-val { font-size:11px; font-weight:500; color:var(--text); margin-bottom:8px; line-height:1.3; }
.content-area p { font-size:12px; line-height:1.5; margin-bottom:6px; }
.content-area strong { color:var(--purple-light); }
.content-area .chart-box { max-width:100%; margin:16px 0; }
.content-area .chart-pair { max-width:100%; display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.content-area .chart-pair .chart-box { max-width:none; }
.content-area table.data { max-width:100%; }
.content-area img { max-width:100%; height:auto; }
.content-area .counter-arg { max-width:100%; }
table.data { width:100%; border-collapse:collapse; margin:8px 0; font-size:10px; font-variant-numeric:tabular-nums; border-top:2px solid #333; border-bottom:1px solid #333; }
.table-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; margin:8px 0; }
table.data th { background:#333333; color:#ffffff; padding:6px 8px; text-align:center; font-weight:600; font-size:10px; }
table.data td { padding:5px 8px; text-align:right; border-bottom:1px solid var(--border); }
table.data td:first-child { text-align:left; font-weight:500; }
table.data tr:nth-child(even) td { background:rgba(124,106,247,0.04); }
table.data .highlight-row td { background:rgba(124,106,247,0.08); font-weight:600; }
.chart-pair { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:16px 0; }
.chart-pair .chart-box { max-width:none; }
.chart-box { background:#ffffff; border:1px solid var(--border); border-radius:2px; padding:12px; max-width:600px; margin:0 auto; }
.chart-box svg { width:100%; height:auto; display:block; max-height:300px; }
.chart-box .chart-title { font-size:12px; color:var(--text-sec); margin-bottom:8px; text-align:center; }
.chart-box svg rect:hover, .chart-box svg circle:hover { opacity:0.8 !important; cursor:pointer; }
.report-img { max-width:100%; height:auto; border-radius:var(--border-radius); margin:12px 0; }
.logo-img { height:40px; width:auto; }
.counter-arg { border-left:3px solid var(--negative); background:#fef2f2; padding:16px 20px; margin:16px 0; border-radius:var(--border-radius); }
.counter-arg .concern-label { color:var(--negative); font-weight:700; font-size:13px; margin-bottom:6px; }
.counter-arg .rebuttal-label { color:var(--positive); font-weight:700; font-size:13px; margin-bottom:6px; }
.callout { background:var(--purple-bg); border-left:3px solid var(--purple); padding:12px 16px; margin:16px 0; border-radius:0 2px 2px 0; }
.callout p { font-size:14px; color:var(--text); margin:0; font-weight:500; }
.expand-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--border-radius); margin:12px 0; overflow:hidden; }
.expand-card:hover { border-color:var(--border2); }
.expand-card .expand-header { padding:14px 18px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; }
.expand-card .expand-header h4 { font-size:14px; font-weight:600; margin:0; }
.expand-card .expand-meta { font-size:12px; color:var(--text-sec); }
.expand-card .expand-arrow { color:var(--purple); font-size:14px; transition:transform 0.3s; }
.expand-card.open .expand-arrow { transform:rotate(90deg); }
.expand-card .expand-body { max-height:0; overflow:hidden; transition:max-height 0.4s ease; }
.expand-card.open .expand-body { max-height:2000px; }
.expand-card .expand-content { padding:0 18px 18px; border-top:1px solid var(--border); }
.scenario-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:16px 0; }
.scenario-card { border-radius:var(--border-radius); padding:20px; border:2px solid; }
.scenario-card.bull { border-color:var(--positive); background:rgba(13,148,136,0.06); }
.scenario-card.base { border-color:var(--purple); background:var(--purple-bg); }
.scenario-card.bear { border-color:var(--negative); background:#fef2f2; }
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:16px 0; }
.metric-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--border-radius); padding:14px; }
.metric-card .mc-label { font-size:11px; color:var(--text-sec); }
.metric-card .mc-value { font-size:20px; font-weight:700; margin:4px 0 2px; }
.report-footer { border-top:2px solid var(--purple); padding:40px 0; margin-top:60px; text-align:center; }
.report-footer .author { font-size:14px; font-weight:700; color:var(--purple); }
.toc { margin:20px 0 40px; padding:24px; background:var(--surface); border:1px solid var(--border); border-radius:var(--border-radius); }
.toc-item { display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dotted var(--border); font-size:13px; }
.toc-item a { color:var(--text); text-decoration:none; }
.toc-item a:hover { color:var(--purple); }
.page-break { position:relative; height:60px; margin:48px 0; display:flex; align-items:center; justify-content:center; }
.page-break::before { content:''; position:absolute; left:10%; right:10%; height:1px; background:linear-gradient(90deg, transparent, var(--purple) 20%, var(--purple) 80%, transparent); }
.page-break .page-label { background:var(--bg); padding:4px 16px; border:1px solid var(--purple); border-radius:16px; color:var(--purple); font-size:10px; font-weight:600; letter-spacing:1px; z-index:1; }
#reading-progress { position:fixed; top:0; left:0; height:3px; width:0%; background:linear-gradient(90deg, var(--purple), var(--positive)); z-index:100; }
.float-toc { position:fixed; right:max(12px, calc((100vw - 960px)/2 - 195px)); top:100px; width:170px; background:rgba(255,255,255,0.95); backdrop-filter:blur(6px); border:1px solid var(--border); border-radius:var(--border-radius); z-index:90; padding:12px; font-size:11px; }
.float-toc a { display:block; padding:4px 8px; color:var(--text-sec); text-decoration:none; border-left:2px solid transparent; }
.float-toc a.active { color:var(--purple); border-left-color:var(--purple); background:var(--purple-bg); }
#back-top { position:fixed; bottom:24px; right:24px; width:40px; height:40px; border-radius:50%; border:1px solid var(--purple); background:rgba(255,255,255,0.9); color:var(--purple); font-size:18px; cursor:pointer; opacity:0; transition:opacity 0.3s; z-index:80; display:flex; align-items:center; justify-content:center; }
#back-top.show { opacity:1; }
#back-top:hover { background:var(--purple); color:#fff; }
.section-dots { position:fixed; left:12px; top:50%; transform:translateY(-50%); z-index:80; display:flex; flex-direction:column; gap:10px; }
.section-dots .dot { width:8px; height:8px; border-radius:50%; background:var(--border); cursor:pointer; transition:all 0.3s; }
.section-dots .dot.active { background:var(--purple); transform:scale(1.6); }
.compliance-notice { background:var(--surface); border:1px solid var(--border); border-radius:var(--border-radius); padding:24px; margin:40px 0; }
.compliance-notice h3 { font-size:16px; margin-bottom:12px; }
.compliance-notice ul { font-size:11px; line-height:1.4; color:var(--text-sec); padding-left:16px; }
.compliance-notice li { margin-bottom:4px; }
.ai-watermark { position:fixed; bottom:8px; left:12px; font-size:10px; color:rgba(124,106,247,0.3); z-index:100; pointer-events:none; }
@media (max-width:1400px) { .float-toc, .section-dots { display:none; } }
@media (max-width:768px) {
  body { font-size:11px; }
  .report { padding:8px; }
  .sidebar-layout { grid-template-columns:1fr; }
  .chart-pair { grid-template-columns:1fr; }
  .content-area .chart-pair { grid-template-columns:1fr; }
  .metric-grid { grid-template-columns:repeat(2,1fr); }
  .scenario-grid { grid-template-columns:1fr; }
  h1 { font-size:28px; } h2 { font-size:18px; }
}
@media (max-width:480px) { table { font-size:9px; } body { font-size:10px; } .sidebar-layout { grid-template-columns:1fr; } .chart-pair { grid-template-columns:1fr; } }
@media print {
  .sticky-header, .float-toc, .section-dots, #reading-progress, #back-top, .ai-watermark { display:none; }
  @page { size:A4; margin:2cm; }
}
"""
