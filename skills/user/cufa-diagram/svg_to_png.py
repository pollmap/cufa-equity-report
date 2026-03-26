#!/usr/bin/env python3
"""
CUFA 다이어그램 SVG → PNG 변환기
Usage:
  python svg_to_png.py input.svg output.png              # 단일 파일
  python svg_to_png.py --batch html_dir/ png_dir/        # 배치 (HTML→PNG)
  python svg_to_png.py --wrap input.svg output.html       # SVG→HTML 래핑만
"""
import subprocess, tempfile, os, sys, shutil

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(SKILL_DIR, "widget_base.css")


def get_css():
    if os.path.exists(CSS_PATH):
        return open(CSS_PATH).read()
    print(f"⚠️ CSS not found at {CSS_PATH}, using inline fallback")
    return """
:root{--p:#E8E6F0;--s:#A09CB0;--t:#706b80;--bg2:#1a1a2e;--b:rgba(255,255,255,0.15)}
body{margin:0;background:#0D0D1A;display:flex;justify-content:center;padding:24px}
.card{background:#161628;border:1px solid #2A2845;border-radius:12px;padding:20px}
svg{font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif}
.th{font-size:14px;font-weight:500;fill:var(--p)}.ts{font-size:12px;fill:var(--s)}.t{font-size:14px;fill:var(--p)}
.arr{stroke:var(--s);stroke-width:1.5}.leader{stroke:var(--t);stroke-width:0.5;stroke-dasharray:3}
.c-purple rect,.c-purple circle{fill:#26215C;stroke:#AFA9EC;stroke-width:0.5}
.c-purple>.th{fill:#CECBF6}.c-purple>.ts{fill:#AFA9EC}
.c-teal rect,.c-teal circle{fill:#04342C;stroke:#5DCAA5;stroke-width:0.5}
.c-teal>.th{fill:#9FE1CB}.c-teal>.ts{fill:#5DCAA5}
.c-blue rect,.c-blue circle{fill:#042C53;stroke:#85B7EB;stroke-width:0.5}
.c-blue>.th{fill:#B5D4F4}.c-blue>.ts{fill:#85B7EB}
.c-green rect,.c-green circle{fill:#173404;stroke:#97C459;stroke-width:0.5}
.c-green>.th{fill:#C0DD97}.c-green>.ts{fill:#97C459}
.c-amber rect,.c-amber circle{fill:#412402;stroke:#EF9F27;stroke-width:0.5}
.c-amber>.th{fill:#FAC775}.c-amber>.ts{fill:#EF9F27}
.c-coral rect,.c-coral circle{fill:#4A1B0C;stroke:#F0997B;stroke-width:0.5}
.c-coral>.th{fill:#F5C4B3}.c-coral>.ts{fill:#F0997B}
.c-red rect,.c-red circle{fill:#501313;stroke:#F09595;stroke-width:0.5}
.c-red>.th{fill:#F7C1C1}.c-red>.ts{fill:#F09595}
.c-pink rect,.c-pink circle{fill:#4B1528;stroke:#ED93B1;stroke-width:0.5}
.c-pink>.th{fill:#F4C0D1}.c-pink>.ts{fill:#ED93B1}
.c-gray rect,.c-gray circle{fill:#2C2C2A;stroke:#B4B2A9;stroke-width:0.5}
.c-gray>.th{fill:#D3D1C7}.c-gray>.ts{fill:#B4B2A9}
"""


def svg_to_html(svg_code, width=720):
    """SVG 코드를 Visualizer 스타일 HTML로 래핑"""
    css = get_css()
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>{css}</style></head><body>
<div class="card" style="width:{width}px;">{svg_code}</div>
</body></html>'''


def svg_to_png(svg_code, output_path, width=720):
    """SVG → HTML → Playwright 스크린샷 → PNG"""
    html = svg_to_html(svg_code, width)

    html_fd, html_path = tempfile.mkstemp(suffix='.html')
    with os.fdopen(html_fd, 'w', encoding='utf-8') as f:
        f.write(html)

    js_code = f'''
const {{ chromium }} = require('playwright');
const fs = require('fs');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage({{
    viewport: {{ width: 800, height: 3000 }},
    deviceScaleFactor: 2
  }});
  await page.setContent(
    fs.readFileSync('{html_path}', 'utf8'),
    {{ waitUntil: 'networkidle' }}
  );
  await page.waitForTimeout(1500);
  const card = await page.$('.card');
  if (!card) {{ console.error('.card not found'); process.exit(1); }}
  await card.screenshot({{ path: '{output_path}', type: 'png' }});
  await browser.close();
}})();
'''
    js_fd, js_path = tempfile.mkstemp(suffix='.js')
    with os.fdopen(js_fd, 'w') as f:
        f.write(js_code)

    try:
        subprocess.run(['node', js_path], check=True,
                       capture_output=True, text=True)
        sz = os.path.getsize(output_path)
        print(f"✅ {output_path} ({sz // 1024}KB)")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        raise
    finally:
        os.unlink(html_path)
        os.unlink(js_path)


def batch_svg_to_png(svg_dict, output_dir, width=720):
    """여러 SVG를 한번에 PNG로 변환
    Args:
        svg_dict: { "01_cover": "<svg>...</svg>", ... }
        output_dir: PNG 출력 폴더
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, svg in svg_dict.items():
        svg_to_png(svg, os.path.join(output_dir, f"{name}.png"), width)
    print(f"\n🎉 {len(svg_dict)}개 PNG 생성 완료 → {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--batch':
        # node batch_screenshot.js로 위임
        js_path = os.path.join(SKILL_DIR, 'batch_screenshot.js')
        subprocess.run(['node', js_path, sys.argv[2], sys.argv[3]])
    elif sys.argv[1] == '--wrap':
        svg = open(sys.argv[2]).read()
        html = svg_to_html(svg)
        with open(sys.argv[3], 'w') as f:
            f.write(html)
        print(f"✅ {sys.argv[3]}")
    else:
        svg = open(sys.argv[1]).read()
        svg_to_png(svg, sys.argv[2])
