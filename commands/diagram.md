# /diagram — Excalidraw 다이어그램 생성

설명을 기반으로 Excalidraw 다이어그램을 생성하여 Obsidian Vault에 저장한다.
Mermaid 대신 시각적으로 깔끔한 Excalidraw 형식 사용.

## 사용법
```
/diagram [설명] [--type flowchart|architecture|sequence|mindmap|er]
```

기본 type: 설명에서 자동 추론

## 다이어그램 타입

### flowchart
프로세스 흐름, 의사결정 트리, 워크플로우

### architecture
시스템 아키텍처, 서비스 연결, 인프라 구성도

### sequence
시간순 상호작용, API 호출 흐름

### mindmap
개념 정리, 브레인스토밍, 계층 구조

### er
데이터 모델, 엔티티 관계도

## 출력

Excalidraw JSON을 `.excalidraw.md` 형식으로 저장:

```
/root/obsidian-vault/03-Resources/diagrams/YYYY-MM-DD-[슬러그].excalidraw.md
```

파일 구조:
```markdown
---
excalidraw-plugin: parsed
tags: [diagram, 타입]
---

# [제목]

==⚠  Switch to MOBILE or MOBILE to mobile view to render the Excalidraw data ==

# Excalidraw Data

## Text Elements
[텍스트 요소들]

## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "luxon-claude-code",
  "elements": [...],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  }
}
```​
```

## Excalidraw 요소 규칙

### 색상 팔레트
- 주요 노드: `#1e1e1e` (텍스트), `#a5d8ff` (배경)
- 연결선: `#868e96`
- 강조: `#ff6b6b` (에러/위험), `#51cf66` (성공)
- 그룹: `#e9ecef` (배경)

### 레이아웃
- 요소 간 최소 간격: 40px
- 텍스트 크기: 제목 24, 본문 16, 라벨 12
- 화살표: `arrow` 타입, `roundness` 적용
- 사각형: `roundness: { type: 3, value: 8 }`

### 연결
- 직선 연결 대신 곡선 화살표 사용
- 바인딩 포인트 자동 계산
- 양방향은 `startArrowhead: "arrow"` + `endArrowhead: "arrow"`

## 예시
```
/diagram Luxon 에이전트 아키텍처 --type architecture
/diagram 카카오톡 메시지 처리 흐름 --type flowchart
/diagram 22B Strategy Engine 데이터 모델 --type er
```

## Obsidian 연동
- 생성된 파일은 Obsidian Excalidraw 플러그인으로 바로 렌더링
- Excalidraw 플러그인 미설치 시 설치 안내 출력
