---
name: research-report-interactive
description: "한국어 연구보고서(.docx) + 인터랙티브 시각화(.html) 통합 스킬. 트리거: '보고서 만들어', '인터랙티브', '시각화', '클릭하면 상세', 'MLA/DSA 스타일', 'HTML로 만들어', '비교연구', '국제비교', 'docx+html', '다이어그램', '차트'. python-docx+matplotlib+lxml로 정부문서형 docx를 생성하고, SVG+JS로 클릭→상세 펼침 인터랙티브 HTML을 만든다. 보고서와 시각화를 동시에 요청하면 두 산출물을 함께 생성한다."
---

# 한국어 연구보고서 + 인터랙티브 시각화 통합 스킬

## 1. 두 가지 산출물

이 스킬은 두 가지를 만든다:
- **Part A**: python-docx 연구보고서 (.docx)
- **Part B**: 인터랙티브 시각화 (.html)

사용자가 둘 중 하나만 요청하면 해당 파트만 실행. 둘 다 요청하면 함께 실행.

---

## Part A: python-docx 연구보고서

### A1. 워크플로우
```
원본 분석 → 마크다운 초안 → 데이터 검증(웹검색) → 차트 생성(matplotlib) → docx 빌드(python-docx) → 각주 삽입(lxml) → 잘림방지(lxml) → 출력
```

### A2. 정부문서형 규격

**폰트/크기:**
| 요소 | 폰트 | 크기 | 색상 | 볼드 |
|------|------|------|------|------|
| Heading 1 (Ⅰ,Ⅱ) | Batang | 13pt | #000000 | ✓ |
| Heading 2 (1,2,3) | Batang | 11pt | #000000 | ✓ |
| Heading 3 (가,나) | Batang | 10pt | #333333 | ✓ |
| 본문 | Batang | 10pt | #333333 | ✗ (볼드 금지) |
| 출처/각주 | Batang | 8pt | #666666 | ✗ |

**페이지 설정 (EMU):**
```python
section.page_width = 7772400
section.page_height = 10058400
section.top_margin = 1143000
section.left_margin = section.right_margin = section.bottom_margin = 914400
```

**East Asian 폰트 필수:**
```python
from docx.oxml.ns import qn
rPr = run._r.get_or_add_rPr()
rFonts = rPr.get_or_add_rFonts()
rFonts.set(qn('w:eastAsia'), 'Batang')
```

### A3. 각주 삽입 (lxml 직접 조작)

python-docx는 각주 미지원. docx를 unzip → XML 수정 → rezip.

**수정할 파일 5개:**
1. `word/footnotes.xml` — 각주 내용 생성
2. `word/document.xml` — 본문에 footnoteReference 삽입
3. `word/styles.xml` — FootnoteReference(위첨자 8pt), FootnoteText 스타일
4. `word/_rels/document.xml.rels` — footnotes.xml 관계 등록
5. `[Content_Types].xml` — ContentType 등록

**키워드 매칭 자동 삽입:**
```python
ref_map = [('키워드', 각주번호), ...]
for kw, fid in ref_map:
    for p in paragraphs:
        if kw in ''.join([t.text for t in p.iter(fn+'t') if t.text]):
            # footnoteReference 요소 삽입
```

### A4. 페이지 잘림 방지
```python
# 표: 행 분할 금지 + 직전 문단 묶기
etree.SubElement(trPr, f'{fn}cantSplit')
etree.SubElement(prev_pPr, f'{fn}keepNext')

# 이미지: keepNext + keepLines
etree.SubElement(pPr, f'{fn}keepNext')
etree.SubElement(pPr, f'{fn}keepLines')
```

### A5. matplotlib 차트

**색상 3색 통일:**
```python
KR = '#E63946'  # 한국 = 빨강
BL = '#4A7FB5'  # 나머지 국가 = 파랑
GR = '#999999'  # OECD 평균 = 회색
```

**규칙:**
- 폰트: NanumGothic, DPI=250, width=Inches(5.0)
- 다이어그램: figsize 8+, pad=15+, 화살표 arrowstyle='->' (꺾쇠 금지)
- 규모 차이 큰 데이터: 패널 분할 (미국만 / 나머지)
- PNG 내부 제목 번호: 반드시 마커 순차에 맞게 재생성

**차트 번호 관리 (중요!):**
```python
markers = re.findall(r'<!-- CHART:g(\w+) -->', content)
for new_idx, old_id in enumerate(markers, 1):
    mapping[old_id] = f'{new_idx:02d}'
# 임시 치환 → 최종 치환 (충돌 방지)
```

### A6. 데이터 검증
- 학술 인용: 저자·연도·저널·권호·페이지 → NBER/RePEc/Scholar 대조
- 거시 데이터: 1차 출처 직접 확인 (한은/국가데이터처/OECD)
- 기관명 변경: 통계청 → 국가데이터처 (2025~)
- **목업 데이터: 절대 금지. 검증된 것만.**

### A7. 인용 규칙
- 외국 저자: 영어 원문 그대로
- 한국 저자: 한글 (주진철·윤혁진(2026))
- 3인 이상: "et al."
- 저서: "in *Title*, pp.XX, Publisher"

---

## Part B: 인터랙티브 시각화 (.html)

### B1. 핵심 설계 원칙

**SVG 시각적 완성도 + 클릭→상세 펼침 = 반드시 합본**

v2(예쁜 SVG but 정적) + v3(클릭 상세 but 못생김) = v4(합본) 패턴을 따른다.
절대로 시각적 완성도를 희생하면서 클릭만 넣지 않는다.

### B2. 클릭→상세 패널 구현 패턴

```javascript
// SVG 내 data-id 속성으로 클릭 대상 지정
function bindClick(svgId, detailId, data) {
  const svg = document.getElementById(svgId);
  const det = document.getElementById(detailId);
  svg.querySelectorAll('[data-id]').forEach(el => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', function() {
      const id = this.getAttribute('data-id');
      const d = data.find(x => x.id === id);
      if (det.classList.contains('open') && det.getAttribute('data-active') === id) {
        det.classList.remove('open');
        return;
      }
      det.innerHTML = `<div class="detail-inner" style="border-left-color:${d.color}">${d.detail}</div>`;
      det.classList.add('open');
      det.setAttribute('data-active', id);
    });
  });
}
```

**CSS 전환:**
```css
.detail { max-height: 0; overflow: hidden; transition: max-height .35s ease; }
.detail.open { max-height: 500px; margin-top: 8px; }
.detail-inner { padding: 10px 12px; border-radius: 8px; background: var(--bg2); border-left: 3px solid var(--bd); font-size: 12px; line-height: 1.7; }
```

### B3. 반응형 필수

```css
@media(max-width:600px) {
  .g2, .g3, .g4 { grid-template-columns: 1fr 1fr }
  body { padding: 8px }
}
@media(max-width:400px) {
  .g2, .g3, .g4 { grid-template-columns: 1fr }
}
.hd h1 { font-size: clamp(16px, 4vw, 20px) }
.card .vl { font-size: clamp(16px, 4vw, 20px) }
```

### B4. 다크모드 필수

```css
:root { --bg:#fff; --redbg:#FCEBEB; --redtx:#791F1F; ... }
@media(prefers-color-scheme:dark) {
  :root { --bg:#1a1a18; --redbg:#351515; --redtx:#f7c1c1; ... }
}
```

### B5. CSS 변수 시스템 (확정판)

```css
--red:#E24B4A; --redbg:#FCEBEB; --redtx:#791F1F;
--blue:#378ADD; --bluebg:#E6F1FB; --bluetx:#0C447C;
--teal:#1D9E75; --tealbg:#E1F5EE; --tealtx:#085041;
--amber:#EF9F27; --amberbg:#FAEEDA; --ambertx:#633806;
--coral:#D85A30; --coralbg:#FAECE7; --coraltx:#712B13;
--purple:#7F77DD; --purplebg:#EEEDFE; --purpletx:#3C3489;
--green:#639922; --greenbg:#EAF3DE; --greentx:#27500A;
--pink:#D4537E; --pinkbg:#FBEAF0; --pinktx:#72243E;
--gray:#888; --graybg:#F1EFE8;
```

각 색상은 3가지: 배경(bg), 테두리/강조(기본), 텍스트(tx).

### B6. SVG 규칙 (HTML 내장용)

```html
<svg viewBox="0 0 720 H" id="..."></svg>
```
- viewBox 너비 720 고정 (width="100%"로 반응형)
- 화살표 마커: `<marker id="aw" ...>` defs에 포함
- 텍스트 클래스: `.sb2`(13px bold), `.st2`(12px), `.ss2`(11px 회색)
- 클릭 대상: `<g data-id="...">`로 감싸기
- fill/stroke: CSS 변수 사용 `fill="var(--redbg)"`

### B7. 시각화 유형별 패턴

**인과 체인:** SVG 박스 + 화살표 마커 + data-id 클릭
**파급경로:** 중앙 박스에서 분기하는 화살표 + 4개 하위 박스
**자산구조:** 쌍방향 수평 바 (왼=부동산, 우=금융) + data-id
**전세 vs HELOC:** 토글 버튼(display:none/block) + SVG 흐름도
**연령별 탄력성:** SVG 막대 차트 + 미국 평균 점선 + data-id
**유동화:** 패널 분할 (미국/기타) SVG
**연금 비교:** JS 탭 전환 + 카드 수치 업데이트 + SVG 바 차트
**자산다변화:** 카드 그리드 + SVG 바 차트
**고령화:** SVG 수평 바 (연도)
**3축 개혁:** SVG 박스+화살표 + 시나리오 A/B/C data-id

### B8. 외부 라이브러리 없음
순수 HTML/CSS/JS만 사용. 어디서든 열림 (로컬, 블로그, Notion 임베드).

---

## Part C: Claude Visualizer (채팅 내 인라인)

### C1. 사용법
```
1. visualize:read_me 호출 (modules: diagram, interactive, chart 등)
2. visualize:show_widget으로 SVG/HTML 렌더링
3. sendPrompt('질문')으로 클릭 시 후속 대화 연결
```

### C2. Visualizer SVG 규칙
- viewBox="0 0 680 H" (680 고정, HTML과 다름!)
- 색상: c-blue, c-red, c-teal 등 테마 클래스
- 텍스트: class="t"(14px), "ts"(12px), "th"(14px bold)
- 클릭: `<g class="node" onclick="sendPrompt('...')">`

---

## Part D: 평가 프레임워크

### 5기준 × 20점
| 기준 | 평가 포인트 |
|------|------------|
| 정보 정확성 | 출처 검증, 목업 제거, 최신 데이터 |
| 시각화 | 색상 통일, 중복 제거, 출처 표기, 잘림 방지 |
| 체계·구조 | 논리 흐름, 연구질문→답 구조 |
| 논리·논증 | 인과관계, 대안 검토, 실증 보강 |
| 독창성 | 독자적 프레임워크, 간접 증거 |

### 외부 평가 반영 프로세스
1. 외부 평가 수령
2. grep -n으로 원본 위치 확인
3. sed/str_replace로 수정
4. docx 재빌드 + 각주 + 잘림방지
5. 수정 전후 대조 검증

---

## Part E: 찬희님 선호

- 목업 데이터 절대 금지
- 색상 3색 통일 (한국=빨강, 나머지=파랑, OECD=회색)
- 그림 번호 순차 (매우 중요)
- 해외 제도: "이름만" 아닌 "작동 원리 + 한국과의 차이"
- 시각화: SVG 완성도 + 클릭 인터랙션 합본 (MLA/DSA 스타일)
- 반응형 + 다크모드 필수
- 한국어 100%
- 인터랙티브: 클릭하면 깊이가 나오는 구조
- 9개국 표기 통일 (한국·미국·일본·영국·프랑스·호주·캐나다·덴마크·스웨덴)
