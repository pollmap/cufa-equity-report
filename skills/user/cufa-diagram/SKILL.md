---
name: cufa-diagram-png
description: CUFA 퍼플 다크 테마 다이어그램/인포그래픽을 SVG로 작성하고 Playwright 브라우저 스크린샷으로 고품질 PNG를 생성하는 스킬. 트리거: '다이어그램 만들어', 'MLA DSA', '인포그래픽', '시각화 PNG', '보고서 다이어그램', '차트 이미지', 'SVG to PNG', '밸류체인', '시스템 아키텍처', '리스크 매트릭스', '피어 비교 표', 'Football Field'. 기업분석보고서, 리서치, 프레젠테이션에 사용할 다크 테마 다이어그램 이미지를 생성한다.
---

# CUFA 다이어그램 PNG 생성 스킬

## 개요

CUFA 퍼플 다크 테마 디자인 시스템 기반으로 SVG 다이어그램을 작성하고,
Playwright 브라우저 렌더링으로 고품질 PNG(Retina 2x)를 생성한다.

**핵심 워크플로우**: SVG 코드 작성 → HTML 래핑 → Playwright 스크린샷 → PNG 출력

## 사전 준비 (최초 1회)

```bash
# 1. Playwright 설치
npm install -g playwright
npx playwright install chromium
npx playwright install-deps chromium

# 2. 한글 폰트 확인
fc-list | grep -i "noto.*cjk"
# 없으면: apt-get install -y fonts-noto-cjk

# 3. 스킬 파일 확인
ls /path/to/cufa-diagram-skill/
# SKILL.md, widget_base.css, screenshot.js, templates/
```

## 디자인 시스템

### 컬러 팔레트

다크 모드 전용. 배경 `#0D0D1A`, 카드 `#161628`, 보더 `#2A2845`.

| 클래스 | 용도 | fill (dark) | stroke | text-th | text-ts |
|--------|------|-------------|--------|---------|---------|
| `c-purple` | 핵심/강조 | `#26215C` | `#AFA9EC` | `#CECBF6` | `#AFA9EC` |
| `c-teal` | 긍정/성장 | `#04342C` | `#5DCAA5` | `#9FE1CB` | `#5DCAA5` |
| `c-blue` | 정보/중립+ | `#042C53` | `#85B7EB` | `#B5D4F4` | `#85B7EB` |
| `c-green` | 수익/개선 | `#173404` | `#97C459` | `#C0DD97` | `#97C459` |
| `c-amber` | 주의/목표 | `#412402` | `#EF9F27` | `#FAC775` | `#EF9F27` |
| `c-coral` | 경쟁/대비 | `#4A1B0C` | `#F0997B` | `#F5C4B3` | `#F0997B` |
| `c-red` | 위험/하락 | `#501313` | `#F09595` | `#F7C1C1` | `#F09595` |
| `c-pink` | 원가/비용 | `#4B1528` | `#ED93B1` | `#F4C0D1` | `#ED93B1` |
| `c-gray` | 중립/구조 | `#2C2C2A` | `#B4B2A9` | `#D3D1C7` | `#B4B2A9` |

### 텍스트 클래스

```
.th  → 14px, font-weight:500, fill:var(--p)  — 제목/강조
.ts  → 12px, font-weight:400, fill:var(--s)  — 설명/보조
.t   → 14px, font-weight:400, fill:var(--p)  — 본문/데이터
```

16px 제목은 inline style: `style="font-size:16px"` on `.th`

### SVG 기본 구조

```svg
<svg width="100%" viewBox="0 0 680 {HEIGHT}">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
      stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>

<!-- 컨텐츠 -->
</svg>
```

- viewBox 너비: **항상 680** (변경 금지)
- viewBox 높이: 컨텐츠에 맞춰 조정 (마지막 요소 + 40px)
- 안전 영역: x=40~640, y=40~(H-40)

### 컬러 클래스 사용법

```svg
<!-- 컬러 박스 -->
<g class="c-purple">
  <rect x="100" y="100" width="200" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="200" y="120" text-anchor="middle" dominant-baseline="central">제목</text>
  <text class="ts" x="200" y="140" text-anchor="middle" dominant-baseline="central">설명 텍스트</text>
</g>

<!-- 화살표 연결 -->
<line x1="200" y1="156" x2="200" y2="180" class="arr" marker-end="url(#arrow)"/>

<!-- 중립 박스 -->
<g class="c-gray">
  <rect x="100" y="180" width="200" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="200" y="206" text-anchor="middle" dominant-baseline="central">중립 항목</text>
</g>
```

**핵심 규칙**:
- `<text>`는 반드시 `<g class="c-xxx">` 직속 자식이어야 색상 적용
- `&` → `&amp;` 필수 (SVG는 XML)
- `dominant-baseline="central"` 사용 시 y 좌표가 박스 중앙
- `text-anchor="middle"` + x를 박스 중앙으로

### 다이어그램 유형별 템플릿

#### 1. MLA (Multi-Layer Architecture) — 밸류체인 계층도

수직 레이어 구조. Layer 1(최하위)부터 Layer N(최상위)까지.
각 레이어: 가로 560px 박스, rx=12, 세로 간격 80~94px.
레이어 간 화살표(↑) 연결. 우측에 시너지/수치 annotation.

```
패턴:
Layer 1 (원자재/인풋)     ← 가장 아래
  ↑
Layer 2 (생산/가공)
  ↑
Layer 3 (브랜드/차별화)
  ↑
Layer 4 (유통/배포)
  ↑
Layer 5 (서비스/최종가치) ← 가장 위 = 최고 부가가치
```

#### 2. DSA (Domain-Specific Architecture) — 시스템 아키텍처

좌→우 흐름. 왼쪽에 입력 요소 4~6개, 중앙에 합산/처리, 우측에 결과 체인.
하단에 타임라인 바.

```
패턴:
[입력A] ─┐
[입력B] ──┼──→ [합산] ──→ [결과1] ──→ [결과2] ──→ [최종]
[입력C] ──┤
[입력D] ─┘
         [────── 타임라인 바 ──────]
```

#### 3. 커버 대시보드

투자의견 + 핵심 지표 + Bull/Base/Bear + 투자포인트 + IS 요약.
그리드 레이아웃.

#### 4. Peer 비교 테이블

텍스트 기반 데이터 그리드. 하이라이트 행에 `c-purple` 배경.

#### 5. Football Field

가로 범위 바. 현재가 기준선(점선). 각 방법론별 색상 바.

#### 6. 리스크 매트릭스

2축(발생확률 × 영향도) 그리드 + 버블 차트.
**주의**: 축 레이블과 데이터 레이블 겹침 방지 — y 좌표 최소 16px 간격.

## PNG 생성 방법

### Step 1: SVG를 HTML로 래핑

```python
import os

CSS_PATH = "/path/to/cufa-diagram-skill/widget_base.css"
css = open(CSS_PATH).read()

def svg_to_html(svg_code, width=720):
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>{css}</style>
</head><body>
<div class="card" style="width:{width}px;">{svg_code}</div>
</body></html>'''

# 파일 저장
html = svg_to_html(my_svg_code)
with open("/tmp/diagram.html", "w") as f:
    f.write(html)
```

### Step 2: Playwright 스크린샷

```javascript
// screenshot.js 사용
const { chromium } = require('playwright');
const fs = require('fs');

async function screenshot(htmlPath, pngPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 800, height: 3000 },
    deviceScaleFactor: 2  // Retina 2x
  });
  const html = fs.readFileSync(htmlPath, 'utf8');
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500); // 폰트 로딩 대기

  const card = await page.$('.card');
  await card.screenshot({ path: pngPath, type: 'png' });
  await browser.close();
}

// 사용
screenshot('/tmp/diagram.html', '/output/diagram.png');
```

### Step 3: 배치 처리 (여러 다이어그램)

```javascript
// batch_screenshot.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function batchScreenshot(htmlDir, pngDir) {
  const browser = await chromium.launch();
  const files = fs.readdirSync(htmlDir)
    .filter(f => f.endsWith('.html')).sort();

  for (const file of files) {
    const page = await browser.newPage({
      viewport: { width: 800, height: 3000 },
      deviceScaleFactor: 2
    });
    const html = fs.readFileSync(path.join(htmlDir, file), 'utf8');
    await page.setContent(html, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    const card = await page.$('.card');
    const pngName = file.replace('.html', '.png');
    await card.screenshot({
      path: path.join(pngDir, pngName),
      type: 'png'
    });
    console.log(`${pngName} done`);
    await page.close();
  }
  await browser.close();
}

const [,, htmlDir, pngDir] = process.argv;
batchScreenshot(htmlDir, pngDir);
```

사용: `node batch_screenshot.js ./html_screens ./output_png`

## Python 헬퍼 (svg_to_png.py)

올인원 스크립트. SVG 문자열 → PNG 파일 직접 생성.

```python
#!/usr/bin/env python3
"""CUFA 다이어그램 SVG → PNG 변환기"""
import subprocess, tempfile, os, sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(SKILL_DIR, "widget_base.css")

def svg_to_png(svg_code, output_path, width=720):
    """SVG 코드를 받아 Playwright로 PNG 스크린샷 생성"""
    css = open(CSS_PATH).read()
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>{css}</style></head><body>
<div class="card" style="width:{width}px;">{svg_code}</div>
</body></html>'''

    with tempfile.NamedTemporaryFile(suffix='.html', mode='w',
                                      delete=False, encoding='utf-8') as f:
        f.write(html)
        html_path = f.name

    js_code = f'''
const {{ chromium }} = require('playwright');
const fs = require('fs');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage({{
    viewport: {{ width: 800, height: 3000 }},
    deviceScaleFactor: 2
  }});
  await page.setContent(fs.readFileSync('{html_path}','utf8'),
    {{ waitUntil: 'networkidle' }});
  await page.waitForTimeout(1500);
  const card = await page.$('.card');
  await card.screenshot({{ path: '{output_path}', type: 'png' }});
  await browser.close();
}})();
'''
    with tempfile.NamedTemporaryFile(suffix='.js', mode='w',
                                      delete=False) as f:
        f.write(js_code)
        js_path = f.name

    subprocess.run(['node', js_path], check=True)
    os.unlink(html_path)
    os.unlink(js_path)
    print(f"✅ {output_path} ({os.path.getsize(output_path)//1024}KB)")


def batch_svg_to_png(svg_dict, output_dir):
    """여러 SVG를 한번에 PNG로 변환
    svg_dict: { "01_cover": "<svg>...</svg>", "02_mla": "<svg>...</svg>" }
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, svg in svg_dict.items():
        svg_to_png(svg, os.path.join(output_dir, f"{name}.png"))


if __name__ == "__main__":
    # CLI: python svg_to_png.py input.svg output.png
    if len(sys.argv) >= 3:
        svg = open(sys.argv[1]).read()
        svg_to_png(svg, sys.argv[2])
```

## 자주 쓰는 패턴

### 데이터 테이블 (Peer 비교 등)

```svg
<!-- 헤더 -->
<text class="ts" x="40" y="70" text-anchor="start">기업</text>
<text class="ts" x="200" y="70" text-anchor="middle">PER</text>
<text class="ts" x="300" y="70" text-anchor="middle">PBR</text>
<line x1="40" y1="76" x2="640" y2="76" stroke="var(--b)" stroke-width="0.5"/>

<!-- 일반 행 -->
<text class="ts" x="40" y="94" text-anchor="start">Caterpillar</text>
<text class="t" x="200" y="94" text-anchor="middle">29.0x</text>
<text class="t" x="300" y="94" text-anchor="middle">N/M</text>

<!-- 하이라이트 행 -->
<g class="c-purple"><rect x="36" y="100" width="608" height="20" rx="4" stroke-width="0"/></g>
<text class="th" x="40" y="114" text-anchor="start">HD건설기계</text>
<text class="th" x="200" y="114" text-anchor="middle">13.85x</text>
```

### 타임라인 바

```svg
<rect x="60" y="424" width="560" height="6" rx="3" fill="var(--bg2)"/>
<rect x="60" y="424" width="140" height="6" rx="3" fill="#7F77DD" opacity="0.6"/>
<rect x="200" y="424" width="180" height="6" rx="3" fill="#5DCAA5" opacity="0.6"/>
<circle cx="60" cy="427" r="5" fill="#7F77DD"/>
<text class="ts" x="60" y="450" text-anchor="start">2026 H1</text>
<text class="ts" x="60" y="464" text-anchor="start">이벤트 설명</text>
```

### 수평 범위 바 (Football Field)

```svg
<!-- 기준선 -->
<line x1="340" y1="110" x2="340" y2="250" stroke="#A78BFA"
  stroke-width="0.8" stroke-dasharray="4"/>
<text class="ts" x="340" y="108" text-anchor="middle">현재 133,000</text>

<!-- 범위 바 -->
<text class="ts" x="84" y="134" text-anchor="end">PER (14~20x)</text>
<g class="c-purple"><rect x="230" y="122" width="254" height="18" rx="4"
  stroke-width="0.5"/></g>
<text class="ts" x="226" y="134" text-anchor="end">125,700</text>
<text class="ts" x="488" y="134" text-anchor="start">179,440</text>
```

### 리스크 매트릭스 버블

```svg
<!-- 그리드 -->
<line x1="160" y1="286" x2="640" y2="286" stroke="#2A2845" stroke-width="0.3"/>
<!-- 영역 색상 -->
<rect x="480" y="286" width="160" height="60" fill="#E24B4A" opacity="0.05"/>
<!-- 버블 -->
<circle cx="400" cy="310" r="22" fill="#FF4D4D" fill-opacity="0.25"
  stroke="#FF4D4D" stroke-width="1"/>
<text x="400" y="306" text-anchor="middle"
  style="font-family:'Noto Sans CJK KR';font-size:11px;font-weight:700;fill:#F09595">PMI</text>
```

## 체크리스트

PNG 생성 전 확인:
- [ ] viewBox 너비 = 680 (절대 변경 금지)
- [ ] 모든 `&` → `&amp;` 처리
- [ ] 모든 `<text>`가 `<g class="c-xxx">` 직속 자식이거나 독립 클래스 보유
- [ ] 겹치는 텍스트 없음 (y 좌표 최소 16px 간격)
- [ ] 화살표 사용 시 `<defs>` 마커 포함
- [ ] Playwright 설치 확인 (`npx playwright install chromium`)
- [ ] 한글 폰트 설치 확인 (`fc-list | grep noto`)
- [ ] `deviceScaleFactor: 2` (Retina 품질)
- [ ] `waitForTimeout(1500)` (폰트 로딩 충분)

## 폴더 구조

```
cufa-diagram-skill/
├── SKILL.md              ← 이 파일
├── widget_base.css       ← 디자인 시스템 CSS
├── screenshot.js         ← Playwright 단일 스크린샷
├── batch_screenshot.js   ← Playwright 배치 스크린샷
├── svg_to_png.py         ← Python 올인원 헬퍼
└── templates/            ← SVG 템플릿 예제
    ├── mla_template.svg
    ├── dsa_template.svg
    ├── cover_template.svg
    ├── peer_table_template.svg
    ├── football_field_template.svg
    └── risk_matrix_template.svg
```

## 미니멀 심볼/아이콘 시스템

SMIC 보고서처럼 밸류체인·제품·산업별 시각 심볼을 SVG로 직접 만든다.
"글만 있으면 상상이 안 된다" — 인간의 시각 인지를 활용.

### 심볼 설계 원칙
1. **미니멀리즘**: 최소한의 선과 면으로 본질을 표현
2. **모노크롬 기반**: 퍼플(#7C6AF7) 단색 + 필요 시 1개 악센트
3. **32×32 ~ 64×64px**: 인라인에 삽입 가능한 크기
4. **재사용 가능**: viewBox 통일 (0 0 64 64)
5. **외부 라이브러리 ZERO**: 순수 SVG path로 구현

### 산업별 심볼 예시

```svg
<!-- 굴착기 (Excavator) -->
<svg viewBox="0 0 64 64" width="48" height="48">
  <rect x="8" y="40" width="48" height="12" rx="3" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <rect x="12" y="44" width="8" height="8" rx="4" fill="#7C6AF7"/>
  <rect x="44" y="44" width="8" height="8" rx="4" fill="#7C6AF7"/>
  <rect x="28" y="28" width="16" height="14" rx="2" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <line x1="36" y1="28" x2="20" y2="12" stroke="#7C6AF7" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="20" y1="12" x2="12" y2="20" stroke="#7C6AF7" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M12 20 L6 24 L14 26 Z" fill="#7C6AF7"/>
</svg>

<!-- 엔진 (Engine) -->
<svg viewBox="0 0 64 64" width="48" height="48">
  <rect x="16" y="16" width="32" height="32" rx="4" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <circle cx="32" cy="32" r="10" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <line x1="32" y1="22" x2="32" y2="26" stroke="#7C6AF7" stroke-width="2"/>
  <line x1="32" y1="38" x2="32" y2="42" stroke="#7C6AF7" stroke-width="2"/>
  <line x1="22" y1="32" x2="26" y2="32" stroke="#7C6AF7" stroke-width="2"/>
  <line x1="38" y1="32" x2="42" y2="32" stroke="#7C6AF7" stroke-width="2"/>
  <rect x="4" y="24" width="12" height="16" rx="2" fill="none" stroke="#A78BFA" stroke-width="1.5"/>
</svg>

<!-- 공장/생산 (Factory) -->
<svg viewBox="0 0 64 64" width="48" height="48">
  <rect x="4" y="28" width="56" height="32" rx="2" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <polygon points="4,28 4,12 16,20 16,28" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <polygon points="16,28 16,12 28,20 28,28" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <polygon points="28,28 28,12 40,20 40,28" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <rect x="48" y="8" width="8" height="20" rx="1" fill="none" stroke="#A78BFA" stroke-width="1.5"/>
</svg>

<!-- 딜러/유통 (Distribution) -->
<svg viewBox="0 0 64 64" width="48" height="48">
  <circle cx="32" cy="20" r="12" fill="none" stroke="#7C6AF7" stroke-width="2"/>
  <circle cx="32" cy="20" r="4" fill="#7C6AF7"/>
  <line x1="32" y1="32" x2="16" y2="48" stroke="#7C6AF7" stroke-width="1.5"/>
  <line x1="32" y1="32" x2="48" y2="48" stroke="#7C6AF7" stroke-width="1.5"/>
  <line x1="32" y1="32" x2="32" y2="52" stroke="#7C6AF7" stroke-width="1.5"/>
  <circle cx="16" cy="48" r="4" fill="none" stroke="#00E09E" stroke-width="1.5"/>
  <circle cx="48" cy="48" r="4" fill="none" stroke="#00E09E" stroke-width="1.5"/>
  <circle cx="32" cy="52" r="4" fill="none" stroke="#00E09E" stroke-width="1.5"/>
</svg>
```

### 사용 패턴

```python
# HTML 보고서 인라인 삽입
ICON_EXCAVATOR = '<svg viewBox="0 0 64 64" width="32" height="32" style="vertical-align:middle;margin-right:8px;">...</svg>'

# 섹션 제목 앞에 아이콘 삽입
h += f'{ICON_EXCAVATOR} <span style="font-size:16px;font-weight:700;">굴착기 사업부</span>'

# 밸류체인 다이어그램 내 아이콘 삽입
# MLA 각 레이어에 해당 심볼을 SVG <use> 또는 인라인으로 배치

# 테이블 첫 컬럼에 아이콘
table_row = f'<td>{ICON_EXCAVATOR} 굴착기</td><td>33,630</td>...'
```

### 범용 산업 심볼 라이브러리 (확장 예정)

| 산업 | 심볼 | 용도 |
|------|------|------|
| 건설기계 | 굴착기, 휠로더, 크레인, 지게차 | HD건설기계 |
| 정유/석화 | 정제탑, 파이프, 탱커, 배럴 | S-Oil 류 |
| 반도체 | 웨이퍼, 칩, PCB, 팹 | 심텍 류 |
| 바이오 | DNA, 분자, 주사기, 임상 | 알지노믹스 류 |
| 금융 | 차트, 코인, 빌딩, 카드 | 키움 류 |
| 통신 | 위성, 안테나, 타워, 신호 | 인텔리안 류 |

**핵심**: 각 종목 보고서마다 해당 산업의 심볼 4~6개를 SVG로 만들어, MLA 다이어그램·섹션 제목·테이블·사이드바에 삽입한다. "글만 있는 보고서"에서 "보는 보고서"로 전환.
