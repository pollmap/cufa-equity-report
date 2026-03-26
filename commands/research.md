# /research — 딥 리서치 파이프라인

주제를 입력하면 체계적으로 질문을 생성하고, 답변을 수집하여 로컬에 저장한다.

## 사용법
```
/research [주제] [--depth shallow|medium|deep] [--questions N]
```

기본값: `--depth medium --questions 10`

## IPO 파이프라인 (Input → Process → Output)

### Step 1: Input (주제 분석)
- 주제의 핵심 키워드 추출
- 관련 하위 분야 파악
- 기존 vault 자료 검색 (`/root/obsidian-vault/03-Resources/`)

### Step 2: Process (질문 생성 → 답변 수집)

depth별 질문 생성 전략:

**shallow** (5개):
- 정의/개요
- 핵심 구성 요소
- 장점/단점
- 현재 트렌드
- 실무 적용법

**medium** (10개):
- shallow 5개 포함
- 기술적 원리
- 경쟁/대안 비교
- 사례 분석
- 미래 전망
- 실행 로드맵

**deep** (20개):
- medium 10개 포함
- 전문가 관점 분석
- 정량적 데이터
- 리스크/제한사항
- 규제/윤리 이슈
- 기존 연구 리뷰
- 반론/비판적 관점
- 구현 상세
- 측정/평가 기준
- 학제간 연결
- 미해결 문제

각 질문에 대해:
1. WebSearch로 최신 정보 수집
2. 수집된 정보 기반 답변 생성
3. 출처 URL 첨부

### Step 3: Output (로컬 저장)

결과를 마크다운 파일로 저장:

```
/root/obsidian-vault/03-Resources/research/YYYY-MM-DD-[주제슬러그].md
```

파일 형식:
```markdown
---
date: YYYY-MM-DD
topic: [주제]
depth: [shallow|medium|deep]
questions: [N]
agent: claude-code
tags: [research, 주제태그]
status: draft
---

# [주제] 리서치

## 개요
[주제 한 줄 요약]

## Q&A

### Q1: [질문]
[답변]
- 출처: [URL]

### Q2: [질문]
...

## 핵심 인사이트
[3-5개 핵심 발견]

## 추가 리서치 필요
[미해결 질문/추가 조사 필요 분야]
```

## 활용

- 저장된 파일은 Obsidian에서 바로 열람 가능
- 다음 리서치의 기반 자료로 활용 (지식 복리 효과)
- `/research [주제] --depth deep`으로 점진적 심화
