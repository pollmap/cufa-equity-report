# 로보티즈 보고서 빌드 + 전송

CUFA 로보티즈(108490) 기업분석보고서를 빌드하고 로컬 PC로 전송한다.

## 1. 빌드

```bash
cd /root/robotis_v7 && python3 build_v6.py
```

## 2. 검증

빌드 후 아래 기준을 충족하는지 자동 검증:
- 글자수 ≥ 38,000
- 테이블 ≥ 55
- 이미지 ≥ 40
- SMIC 표절 키워드 부재
- 파일 존재 + 크기 확인

검증 코드:
```python
python3 -c "
from docx import Document
import os
path = '/root/robotis_v7/CUFA_ROBOTIS_v9.docx'
doc = Document(path)
total_text = ''.join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            total_text += cell.text
char_count = len(total_text)
table_count = len(doc.tables)
image_count = sum(1 for rel in doc.part.rels.values() if 'image' in rel.reltype)
fsize = os.path.getsize(path)
print(f'글자수: {char_count:,} (pass: {char_count >= 38000})')
print(f'테이블: {table_count} (pass: {table_count >= 55})')
print(f'이미지: {image_count} (pass: {image_count >= 40})')
print(f'파일크기: {fsize//1024}KB')
"
```

## 3. 로컬 PC 전송

유저의 Windows PC로 SCP 전송:
```bash
scp root@62.171.141.206:/root/robotis_v7/CUFA_ROBOTIS_v9.docx C:\Users\lch68\Desktop\
```
> 이 명령은 **유저의 로컬 터미널(PowerShell/CMD)**에서 실행해야 함.
> VPS에서 실행하는 게 아님!

## 4. 파일 구조

```
/root/robotis_v7/
├── build_v6.py              # 메인 빌드 스크립트 (유일한 수정 대상)
├── company_profile.json     # 종목 데이터
├── charts/                  # 차트 이미지 45개+
│   ├── A1_stock_vs_kosdaq.png
│   ├── B1_global_robot_market.png
│   └── ...
└── CUFA_ROBOTIS_v9.docx     # 최종 출력
```

## 5. 버전 히스토리

| 버전 | 주요 변경 |
|------|-----------|
| v8_final | SMIC 2열 사이드바 + 30,000자+ + Q&A 통합 |
| v9 | 표 축소(7/6.5pt+tcMar), 1열→2열 전환(22개 P_→10개 sidebar_block), 표지 보강(IS라벨+작성자2행+투자포인트 확장), 목차 점선, 차트 크기 통일(70/78mm), H_ 크기/간격, P_ 줄간격 14pt, 공백 제거 |

## 6. 핵심 헬퍼 함수 (build_v6.py)

- `sidebar_block(doc, sidebar_items, body_texts, charts)` — SMIC 2열 블록
- `TBL(doc, headers, rows)` — 보라색 테이블
- `pair(doc, f1, c1, f2, c2)` — 차트 2개 나란히
- `P_(doc, text, ...)` — 본문 단락
- `H_(doc, text, level)` — 제목 (level 1=14pt, 2=11pt)
- `PB(doc)` — 페이지 브레이크
