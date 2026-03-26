---
name: bok-report-writing
description: "한국어 사전조사/연구보고서 작성 스킬. 마크다운 먼저 충분히 작성(40,000자+) → 품질 검증 → docx 빌드(보라 테마, 맑은 고딕, 차트 인라인). 트리거: '보고서 만들어', '사전조사', '문서 작성', '리포트', '팀원에게 공유', '경시대회 보고서', 'docx 만들어', '분석 보고서'. 핵심 원칙: 글이 본론, 시각자료가 보조. 목업 데이터 금지. 처음 보는 사람도 이해 가능. 용어 반드시 정의."
---

# 한국어 사전조사/연구보고서 작성 스킬

## 1. 핵심 철학

- 글이 본론, 시각자료(차트/표)가 보조
- 처음 보는 사람도 바로 이해 가능해야 함
- 목업 데이터 절대 금지. 검증된 것만 사용
- 용어가 처음 나올 때 반드시 괄호 설명
- 볼드(**) 남발 금지. 핵심 포지션·결론에만 사용하되, 사용자가 제거 요청 시 전부 제거
- "우리"가 아닌 작성자 이름으로 서술 (개인 연구 톤)

## 2. 워크플로우 (5단계)

```
[1단계] 리서치 → [2단계] 마크다운 작성(40,000자+) → [3단계] 품질 검증 → [4단계] docx 빌드 → [5단계] 피드백 반영
```

### 2.1 [1단계] 리서치 선행

- web_search 영어/일본어 우선
- 1차 출처 확보: 학술(NBER, IMF, BIS), 기관(IEA, EIA, 한은 ECOS), 보도(CNBC, Bloomberg, Reuters)
- 팩트 교차검증: 날짜, 수치, 출처명 정확성 확인
- 최소 20개 이상 참고문헌

### 2.2 [2단계] 마크다운 먼저 (핵심)

마크다운을 충분히(최소 40,000자) 작성한 후 docx로 변환한다. 절대로 docx부터 만들지 않는다.

파트별 분할 작성:
```
report_part1.md → 도입부, 배경 (~8,000자)
report_part2.md → 포지션, 기본개념 (~8,000자)
report_part3.md → 데이터, 전쟁 상세 (~13,000자)
report_part4.md → 취약성, 전이 메커니즘 (~13,000자)
report_part5.md → 금리, 논거, 제언, 결론, 참고문헌 (~12,000자)

cat part1 part2 part3 part4 part5 > 최종.md
```

각 파트 작성 후 글자 수 확인:
```bash
wc -c /home/claude/report_part1.md
```

### 2.3 [3단계] 품질 검증 (Python 자동화)

마크다운 완성 후 다음을 검증한다:

```python
# 1. ** 볼드 잔여 확인
count = text.count('**')

# 2. 중복 서술 검출
for pattern in known_duplicates:
    if text.count(pattern) > 1:
        flag(pattern)

# 3. 비문 패턴 검출
problematic = [
    ('25%+ 가', '띄어쓰기'),
    ('이다. 구체적으로', '어색한 연결'),
]

# 4. 섹션 간 브릿지 문장 확인
# 각 ## 섹션 끝에 다음 섹션으로 연결하는 문장이 있는지 검사

# 5. 용어 첫 등장 시 정의 여부
terms = ['CPI', 'PPI', 'CSI', 'DSR', 'K-dot', 'Forward Guidance', 
         '디앵커링', '삼위일체', 'Taylor Rule']
for term in terms:
    first_pos = text.find(term)
    context = text[first_pos:first_pos+200]
    if '(' not in context and ':' not in context:
        flag(f'{term} 정의 없음')
```

### 2.4 [4단계] docx 빌드 (docx-js, Node.js)

```bash
npm install docx
node build_report.js
```

디자인 규격:

| 요소 | 규격 |
|------|------|
| 폰트 | 맑은 고딕 (한글 깨짐 방지) |
| 본문 크기 | 10pt (size: 20) |
| Heading 1 | 15pt, 보라(#7C6AF7), bold, 하단 보라 라인 |
| Heading 2 | 12pt, 다크(#1A1A2E), bold, ▎ 보라 마커 |
| 표 헤더 | 보라 배경(#7C6AF7) + 흰 글씨 |
| 표 행 | 짝수행 연보라(#F0EEFF) 줄무늬 |
| 인용문 | 연보라 배경 음영 |
| 킬러 인용 | 연빨강 배경 + 빨간 글씨(#E63946) |
| 헤더 | 오른쪽 정렬, 보라색, 제목 |
| 푸터 | 중앙 정렬, 작성자 + 보라 페이지 번호 |
| 페이지 | A4 (11906x16838 DXA), 여백 1200 |
| 줄간격 | 360 (1.5배) |
| 문단 간격 | after: 120 |

색상 시스템:
```javascript
const P = "7C6AF7";    // 메인 보라
const PD = "5B4CC4";   // 다크 보라
const PL = "F0EEFF";   // 연보라 배경
const D = "1A1A2E";    // 다크 텍스트
const G = "888888";    // 회색
const R = "E63946";    // 빨간 액센트
const W = "FFFFFF";    // 흰색
```

차트 삽입:
```javascript
// PNG를 Buffer로 읽어서 ImageRun으로 삽입
const charts = {};
for (const name of chartNames) {
  charts[name] = fs.readFileSync(`/mnt/user-data/uploads/${name}.png`);
}

function img(name, w=540, h=270) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({ 
      data: charts[name], 
      transformation: { width: w, height: h } 
    })]
  });
}
```

표 구현:
```javascript
function tbl(headers, rows) {
  const w = Math.floor(9200 / headers.length);
  const hCells = headers.map(h => new TableCell({
    shading: { fill: P, type: ShadingType.CLEAR },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: h, bold: true, size: 18, font: FONT, color: W })]
    })]
  }));
  // 짝수행 줄무늬
  const dRows = rows.map((r, ri) => new TableRow({
    children: r.map(c => new TableCell({
      shading: ri % 2 === 0 ? { fill: PL, type: ShadingType.CLEAR } : {},
      children: [new Paragraph({
        children: [new TextRun({ text: String(c), size: 18, font: FONT, color: D })]
      })]
    }))
  }));
  return new Table({
    width: { size: 9200, type: WidthType.DXA },
    rows: [new TableRow({ children: hCells })].concat(dRows)
  });
}
```

마크다운→docx 파싱:
```javascript
// 마크다운을 줄 단위로 읽으며 docx 요소로 변환
const lines = md.split('\n');
for (const line of lines) {
  if (line.startsWith('## Ⅰ')) → h1()
  if (line.startsWith('### ')) → h2()
  if (line.startsWith('| ')) → 표 수집 → tbl()
  if (line.includes('[그림') && line.includes('차트 c')) → img() + note()
  if (line.startsWith('> ')) → quote() 또는 redQuote()
  else → p()
}
```

### 2.5 [5단계] 피드백 반영

사용자 피드백 패턴과 대응:

| 피드백 | 대응 |
|--------|------|
| "텍스트 너무 적어" | 마크다운 파트별 확장. 그래프 "읽는 법" 추가. 배경지식 보강. |
| "** 없애" | `text.replace('**', '')` |
| "한글 깨짐" | 폰트를 맑은 고딕으로 변경 |
| "디자인 바꿔" | 색상 시스템 변경 (보라/파랑/초록 등) |
| "목차 없어" | pandoc --toc 또는 docx-js 수동 목차 |
| "우리→나" | "우리"를 작성자 이름으로 치환 |
| "중복이 많아" | Python 중복 검출 → 그래프 설명에 통합하고 중복 문단 제거 |
| "연결이 끊김" | 섹션 끝에 브릿지 문장 추가 ("그렇다면 다음 질문은...") |

## 3. 마크다운 작성 규칙

### 3.1 구조

```markdown
# 제목

작성자: OOO
작성일: YYYY년 M월 D일

---

## 목차
Ⅰ. ...
Ⅱ. ...

---

## Ⅰ. 섹션 제목

### 1. 소섹션 제목

본문 텍스트...

| 표 헤더1 | 표 헤더2 |
|----------|----------|
| 데이터 | 데이터 |

[그림 N] 제목 (차트 c1_xxx 참조)

> 인용문

---

## 참고문헌

### 학술
1. ...

### 기관
N. ...

### 보도
N. ...

### 데이터
N. ...
```

### 3.2 그래프/표 설명 패턴 (핵심)

모든 그래프에 다음 3가지를 포함해야 한다:

1. "이 그래프를 읽는 법": 가로축, 세로축, 선 색상, 단위 설명
2. "핵심 구간 해설": 가장 중요한 구간을 지적하고 의미 설명
3. "지금 시점에서 중요한 것": 현재 상황에서 이 그래프가 무엇을 말하는지

예시:
```
[그림 N] Taylor Rule 적정 금리 (차트 c9_taylor_rule 참조)

이 그래프를 읽는 법: 가로축은 시간, 세로축은 금리(%)다. 
파란선이 Taylor Rule 계산값(적정), 빨간 점선이 실제 기준금리다.

파란선이 빨간 점선보다 위에 있으면 "금리가 너무 낮다"는 뜻이고, 
아래에 있으면 "금리가 너무 높다"는 뜻이다.

2022년을 보면, CPI가 5%대까지 치솟으면서 파란선(적정)이 4%+까지 
올라갔다. 한은은 3.50%까지 올렸지만 파란선에 못 미쳤다.

현재 시점: 파란선 2.25%, 빨간 점선 2.50%. 동결 합리적. 
그러나 CPI 3.2%→파란선 3.10%로 급등. 인상 프레임 진입.
```

### 3.3 용어 정의 패턴

처음 등장하는 용어는 반드시 괄호 안에 정의:

```
IRGC(이란 혁명수비대: Islamic Revolutionary Guard Corps, 이란의 정예 군사 조직)
Forward Guidance(선제적 안내: 중앙은행이 향후 정책 방향을 미리 시장에 알려 기대를 조율하는 기법)
디앵커링(de-anchoring, 기대 이탈: 소비자들이 중앙은행의 2% 목표를 더 이상 믿지 않게 되는 현상)
```

2회차 이후 등장 시에는 약어만 사용:
```
IRGC는 3월 2일 해협을 공식 봉쇄했다.
```

### 3.4 섹션 간 브릿지 문장

각 섹션 마지막에 다음 섹션으로 연결하는 1~2문장 필수:

```
이것이 2008년과 2026년의 결정적 차이다. 
그렇다면 이 충격이 한국에 왜 특별히 위험한가? 
그것은 한국 경제의 구조적 취약성에 있다.
```

### 3.5 비문 방지 체크리스트

- [ ] "이다. 구체적으로" → "이며," 로 자연스럽게 연결
- [ ] 숫자 근거 반드시 명시 (예: "4.8배" → "월 15만x12=180만 vs 월 3.1만x12=37.5만. 180/37.5=4.8")
- [ ] 같은 인용(기관/인물) 3회 이상 반복 금지
- [ ] 띄어쓰기: "25%+ 가" → "25% 이상이"
- [ ] 그래프 설명 안에 쓴 내용을 밖에서 다시 쓰지 않기

## 4. docx 표지 패턴

```javascript
// 표지
children.push(new Paragraph({ spacing: { before: 2400 }, children: [] }));
children.push(/* 대회명/기관명 - 회색 22pt */);
children.push(/* 부제목 - 보라 40pt bold */);
children.push(/* ━━━ 보라 구분선 */);
children.push(/* 메인 제목 - 다크 34pt bold */);
children.push(/* 설명 - 회색 20pt */);
children.push(/* 날짜 - 회색 20pt */);
children.push(/* 작성자 - 회색 20pt */);
children.push(/* 수신인 - 회색 16pt */);
children.push(pb());
```

## 5. 참고문헌 작성 규칙

- 외국 저자: 영어 원문 그대로 (Brandão-Marques, L. et al.)
- 한국 저자: 한글 (주진철·윤혁진)
- 3인 이상: "et al."
- 분류: 학술 / 기관 / 보도·분석 / 데이터 4개 카테고리
- 번호: 전체 통번
- 최소 20개, 목표 30개

## 6. 품질 기준

| 기준 | 최소 | 목표 |
|------|------|------|
| 글자 수 | 30,000자 | 40,000자+ |
| 참고문헌 | 20개 | 30개+ |
| 그래프 "읽는 법" | 모든 그래프 | 모든 그래프 |
| 용어 정의 | 주요 10개 | 모든 전문용어 |
| 브릿지 문장 | 주요 전환점 | 모든 섹션 끝 |
| 중복 서술 | 0건 | 0건 |
| ** 볼드 | 사용자 요청 시 0 | 최소화 |
| 비문 | 0건 | 0건 |

## 7. 안티패턴 (하지 말 것)

1. docx부터 만들지 마라. 마크다운이 먼저다.
2. 10,000자짜리 보고서를 만들고 "충분하다"고 하지 마라. 최소 30,000자.
3. 그래프를 넣고 설명 없이 넘어가지 마라. "읽는 법"이 필수.
4. 같은 데이터를 그래프 설명과 본문에서 두 번 쓰지 마라. 한 곳에 통합.
5. 용어를 정의 없이 쓰지 마라. 처음 나올 때 반드시 괄호 설명.
6. Arial/Batang 폰트를 쓰지 마라. 한글 깨진다. 맑은 고딕을 써라.
7. 섹션이 끊기면서 다음 섹션으로 갑자기 넘어가지 마라. 브릿지 문장 필수.
