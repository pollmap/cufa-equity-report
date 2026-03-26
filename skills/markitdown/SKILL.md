---
name: markitdown
description: "Microsoft MarkItDown — 모든 파일을 깨끗한 마크다운으로 변환. PDF, DOCX, PPTX, XLSX, HTML, 이미지(OCR), 오디오(STT), YouTube(자막), ZIP, EPub, Outlook MSG 등 10+ 포맷 지원. CLI + Python API. 트리거: 'markitdown', '파일 변환', '마크다운으로 변환', 'PDF를 마크다운으로', '문서 변환', 'pptx 읽어', 'docx 읽어', 'xlsx 읽어', '파일 내용 추출', 'convert to markdown', '이 파일 읽어줘', 'YouTube 자막 추출', '파일 파싱'. 파일을 LLM이 읽기 좋은 마크다운으로 변환할 때 사용."
---

# MarkItDown — 만능 파일→마크다운 변환기

## 1. 개요

Microsoft 오픈소스. 모든 파일을 깨끗한 마크다운으로 변환.
LLM에 파일 내용을 넘기기 전 전처리에 최적.

## 2. 지원 포맷

| 포맷 | 확장자 | 비고 |
|------|--------|------|
| PDF | .pdf | pdfminer 기반, Azure Doc Intel 옵션 |
| Word | .docx | mammoth 기반 |
| PowerPoint | .pptx | python-pptx |
| Excel | .xlsx, .xls | 시트별 테이블 변환 |
| HTML | .html | 클린 마크다운 변환 |
| 이미지 | .jpg, .png 등 | EXIF 메타데이터 + OCR 플러그인 |
| 오디오 | .wav, .mp3 | 음성→텍스트 변환 |
| YouTube | URL | 자막 추출 |
| ZIP | .zip | 내부 파일 순회 변환 |
| EPub | .epub | 전자책 변환 |
| Outlook | .msg | 이메일 메시지 |
| 텍스트 | .csv, .json, .xml | 그대로 또는 구조화 |

## 3. CLI 사용법

```bash
# 기본 변환
markitdown file.pdf > output.md

# 출력 파일 지정
markitdown file.pptx -o output.md

# stdin 파이프
cat file.docx | markitdown

# 여러 파일 변환 (배치)
for f in *.pdf; do markitdown "$f" -o "${f%.pdf}.md"; done
```

## 4. Python API

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("file.pdf")
print(result.text_content)
```

### 4.1 LLM 이미지 설명 연동

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("image.jpg")
print(result.text_content)
```

### 4.2 YouTube 자막 추출

```python
md = MarkItDown()
result = md.convert("https://www.youtube.com/watch?v=VIDEO_ID")
print(result.text_content)
```

## 5. 워크플로우 패턴

### 5.1 파일 → LLM 분석

```bash
# 1. 파일을 마크다운으로 변환
markitdown report.pdf -o report.md

# 2. 변환된 마크다운을 Read 도구로 읽기
# 3. LLM이 분석/요약/번역
```

### 5.2 배치 변환

```bash
# 폴더 내 모든 문서를 마크다운으로
for f in docs/*; do
  markitdown "$f" -o "converted/$(basename "${f%.*}").md"
done
```

### 5.3 다른 스킬과 연동

- **Obsidian Vault**: 변환된 마크다운을 vault에 Literature Note로 저장
- **NotebookLM Pipeline**: 변환 후 NotebookLM에 소스로 추가
- **Think Tank**: 변환된 콘텐츠를 인테이크 모드로 분석
- **Deep Research**: 로컬 문서를 리서치 소스로 활용

## 6. 실행 전 체크

```bash
# 설치 확인
python3 -c "from markitdown import MarkItDown; print('OK')"

# CLI 확인
markitdown --help
```

미설치 시: `python3 -m pip install 'markitdown[all]'`

## 7. 주의사항

- 이미지 OCR은 markitdown-ocr 플러그인 필요 (`pip install markitdown-ocr`)
- 오디오 변환은 ffmpeg 필요 (미설치 시 경고 표시)
- 대용량 PDF는 Azure Document Intelligence 사용 권장
- YouTube는 자막이 있는 영상만 지원
