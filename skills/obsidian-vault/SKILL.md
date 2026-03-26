---
name: obsidian-vault
description: "Obsidian 지식 베이스 관리 스킬. 리서치 결과를 구조화된 마크다운으로 vault에 저장. [[wikilinks]], YAML 프론트매터, 태그 체계, MOC(Map of Content) 자동 생성. obsidian-headless로 동기화/퍼블리시. 트리거: 'obsidian', '옵시디언', 'vault', '볼트', '지식 베이스', 'knowledge base', '노트 정리', '제텔카스텐', 'zettelkasten', 'PKM', '노트 만들어', 'vault에 저장', '옵시디언에 넣어', 'wikilink', '링크 노트', 'MOC', 'Map of Content', '노트 동기화', '퍼블리시'. vault 경로 미설정 시 초기화."
---

# Obsidian Vault 지식 베이스 관리

## 1. 핵심 원리

- Obsidian vault = 폴더 안의 마크다운 파일. Claude Code가 직접 읽고 쓸 수 있음.
- 모든 노트는 **YAML 프론트매터 + 본문 + wikilinks** 구조.
- 지식은 MOC(Map of Content)로 계층화.
- 원자적 노트 원칙: 하나의 노트 = 하나의 아이디어/개념.

## 2. Vault 초기화

최초 실행 시 사용자에게 확인:

1. Vault 경로 (기본: `~/obsidian-vault/`)
2. 기존 vault가 있으면 구조 분석 후 적응
3. 새 vault면 기본 구조 생성:

```
vault/
├── 00-inbox/          # 미분류 노트
├── 01-fleeting/       # 임시 메모
├── 10-literature/     # 책/기사/논문 노트
├── 20-permanent/      # 영구 노트 (내 생각)
├── 30-projects/       # 프로젝트별 노트
├── 40-areas/          # 관심 분야별
├── 90-templates/      # 노트 템플릿
├── 95-MOC/            # Map of Content
└── 99-attachments/    # 이미지, PDF 등
```

## 3. 노트 생성 규칙

### 3.1 YAML 프론트매터 (필수)

```yaml
---
title: 노트 제목
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
type: fleeting/literature/permanent/project/moc
source: 출처 URL 또는 참조
status: draft/review/final
---
```

### 3.2 본문 구조

```markdown
# 제목

## 핵심 요약
한 문단으로 핵심 아이디어.

## 상세 내용
...

## 내 생각
이 내용에 대한 나의 해석/비판/연결.

## 연결
- [[관련노트1]] — 연결 이유
- [[관련노트2]] — 연결 이유

## 참고
- [출처](URL)
```

### 3.3 Wikilink 규칙

- 다른 노트 참조 시 반드시 `[[노트명]]` 사용.
- 특정 섹션 참조: `[[노트명#섹션]]`
- 별칭 사용: `[[노트명|표시할 텍스트]]`
- 새 노트로 이어질 링크도 미리 생성 (빈 링크 OK).

## 4. 리서치 → Vault 파이프라인

사용자가 주제를 주면:

1. **WebSearch/WebFetch로 리서치** 수행.
2. 소스별 **Literature Note** 생성 (`10-literature/`).
3. 핵심 인사이트를 **Permanent Note**로 추출 (`20-permanent/`).
4. 관련 MOC 업데이트 (`95-MOC/`).
5. 기존 노트와의 연결(wikilinks) 자동 탐색.

```
WebSearch → Literature Notes → Permanent Notes → MOC 업데이트
                                     ↓
                              기존 노트와 [[연결]]
```

## 5. MOC (Map of Content) 관리

MOC는 특정 주제의 노트들을 조감하는 인덱스 파일:

```markdown
---
title: AI MOC
type: moc
updated: 2026-03-23
---

# AI Map of Content

## 기초 개념
- [[트랜스포머 아키텍처]]
- [[어텐션 메커니즘]]

## 실용 도구
- [[Claude Code 활용법]]
- [[MCP 서버 패턴]]

## 트렌드
- [[2026 AI 에이전트 동향]]

## 미분류
- [[임시 AI 메모 1]]
```

새 노트 생성 시 해당 MOC에 자동 추가.

## 6. Obsidian Headless 연동

vault를 Obsidian Sync/Publish와 동기화:

```bash
# 동기화 (로컬 ↔ 클라우드)
ob sync --vault /path/to/vault

# 지속 동기화 (watch 모드)
ob sync --vault /path/to/vault --continuous

# 퍼블리시 (웹 공개)
ob publish --vault /path/to/vault
```

## 7. Think Tank 연동

Think Tank 스킬과 함께 사용 시:

- Think Tank 세션 요약 → Vault의 `01-fleeting/` 에 자동 저장.
- Think Tank 의사결정 로그 → `30-projects/decisions/` 에 저장.
- Think Tank 도메인 지식 → Vault의 `40-areas/` 와 동기화.

## 8. NotebookLM 연동

NotebookLM Pipeline 스킬과 함께:

- Vault 노트를 NotebookLM 소스로 일괄 추가.
- NotebookLM 생성 보고서를 Vault에 Literature Note로 저장.
- 퀴즈/플래시카드를 Vault의 학습 노트로 변환.

## 9. 검색 및 탐색

Vault 내 검색은 Claude Code 도구로 직접:

```
Grep: vault 내 키워드 검색
Glob: 특정 패턴의 노트 찾기
Read: 노트 내용 읽기
```

태그 기반 탐색:
```bash
# 특정 태그의 노트 찾기
grep -r "tags:.*투자" vault/ --include="*.md"
```
