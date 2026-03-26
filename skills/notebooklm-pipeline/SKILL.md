---
name: notebooklm-pipeline
description: "NotebookLM 자동화 파이프라인. notebooklm-py를 활용한 콘텐츠 생성 — 소스 인제스트(URL/PDF/YouTube) → 노트북 생성 → 콘텐츠 생성(오디오 팟캐스트, 비디오, 슬라이드, 인포그래픽, 퀴즈, 보고서, 마인드맵). 트리거: 'notebooklm', '노트북lm', '팟캐스트 만들어', '오디오 요약', '슬라이드 만들어', '퀴즈 만들어', '콘텐츠 변환', '리서치 자동화', '소스 인제스트', '영상 요약', 'YouTube 정리', 'PDF 정리', '학습 자료 만들어', '플래시카드'. notebooklm-py 미설치 시 설치 안내."
---

# NotebookLM 자동화 파이프라인

## 1. 개요

Google NotebookLM의 기능을 notebooklm-py 라이브러리로 자동화.
소스를 넣으면 → 팟캐스트, 슬라이드, 퀴즈, 보고서 등 9종 콘텐츠를 자동 생성.

**주의**: 비공식 API 사용. 연구/프로토타이핑/개인 용도에 적합. 프로덕션 비권장.

## 2. 사전 요구사항 체크

실행 전 반드시 확인:

```bash
# 설치 확인
pip show notebooklm-py

# 미설치 시
pip install notebooklm-py

# 로그인 (최초 1회)
notebooklm login
```

로그인이 안 되어 있으면 사용자에게 `! notebooklm login` 실행을 안내.

## 3. 워크플로우

```
[소스 수집] → [노트북 생성] → [소스 추가] → [콘텐츠 생성] → [다운로드/내보내기]
```

### 3.1 소스 수집

사용자가 제공한 소스를 유형별로 분류:

| 유형 | 예시 | CLI 명령 |
|------|------|----------|
| URL | 웹 기사, 블로그 | `notebooklm source add --url URL` |
| YouTube | 영상 링크 | `notebooklm source add --youtube URL` |
| PDF | 로컬 파일 | `notebooklm source add --pdf path` |
| 텍스트 | 직접 입력 | `notebooklm source add --text "내용"` |
| Google Drive | 드라이브 파일 | `notebooklm source add --drive FILE_ID` |

### 3.2 노트북 생성

```bash
# 새 노트북 생성
notebooklm create --name "프로젝트명"

# 기존 노트북 목록
notebooklm list
```

### 3.3 콘텐츠 생성 (9종)

| 콘텐츠 | 명령 | 출력 |
|--------|------|------|
| **오디오 팟캐스트** | `notebooklm generate audio --wait` | MP3/MP4 |
| **비디오 오버뷰** | `notebooklm generate video --style cinematic` | MP4 |
| **슬라이드** | `notebooklm generate slides --mode detailed` | PDF/PPTX |
| **인포그래픽** | `notebooklm generate infographic` | PNG |
| **퀴즈** | `notebooklm generate quiz --difficulty medium` | JSON/MD/HTML |
| **플래시카드** | `notebooklm generate flashcards` | JSON/MD |
| **보고서** | `notebooklm generate report --type briefing` | Markdown |
| **데이터 테이블** | `notebooklm generate table --spec "비교표"` | CSV |
| **마인드맵** | `notebooklm generate mindmap` | JSON |

### 3.4 배치 파이프라인

여러 소스 → 여러 콘텐츠를 한 번에:

```bash
# 예: 논문 3개 → 팟캐스트 + 퀴즈 + 보고서
notebooklm create --name "논문리뷰"
notebooklm source add --url URL1 --url URL2 --pdf paper3.pdf
notebooklm generate audio --wait
notebooklm generate quiz --difficulty hard --export json
notebooklm generate report --type study-guide
```

## 4. Python API 활용 (고급)

CLI 대신 Python async API로 더 세밀한 제어:

```python
import asyncio
from notebooklm import NotebookLM

async def pipeline():
    async with NotebookLM() as nlm:
        nb = await nlm.create_notebook("리서치")
        await nb.add_source(url="https://...")
        await nb.add_source(youtube="https://...")

        # 채팅으로 질문
        answer = await nb.chat("핵심 논점 3가지 정리해줘")

        # 오디오 생성
        audio = await nb.generate_audio(format="conversation", length="short")
        await audio.download("output.mp3")

        # 퀴즈 생성
        quiz = await nb.generate_quiz(difficulty="hard")
        quiz.export_json("quiz.json")

asyncio.run(pipeline())
```

## 5. 리서치 에이전트 활용

```bash
# 웹 리서치 (fast/deep)
notebooklm research --query "주제" --mode deep

# Google Drive 리서치
notebooklm research --drive --query "관련 문서"
```

리서치 결과는 자동으로 노트북에 소스로 추가됨.

## 6. 출력 관리

- 생성된 파일은 현재 디렉토리 또는 사용자 지정 경로에 저장.
- `--output` 플래그로 저장 경로 지정 가능.
- Think Tank 연동 시 `think-tank/domains/` 하위에 저장 권장.
- Obsidian Vault 연동 시 vault 폴더에 마크다운 보고서 직접 저장 가능.

## 7. 에러 핸들링

| 에러 | 원인 | 해결 |
|------|------|------|
| 401 Unauthorized | 로그인 만료 | `notebooklm login` 재실행 |
| Rate limit | 요청 과다 | 30초 대기 후 재시도 |
| Generation timeout | 대용량 소스 | `--wait --timeout 300` 으로 타임아웃 연장 |
| Source rejected | 지원 안 되는 형식 | 텍스트로 변환 후 `--text`로 추가 |
