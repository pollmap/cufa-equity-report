# /self-improve — 자기개선 루프

사용자의 교정사항을 기록하고, 반복 패턴을 영구 규칙으로 승격시킨다.

## 사용법
```
/self-improve [기록|승격|목록]
```

## 워크플로우

### 1. 교정 기록 (`/self-improve 기록` 또는 인자 없이)

사용자가 방금 교정한 내용을 분석하여 피드백 메모리에 저장한다.

- 현재 대화에서 사용자가 수정/거부/교정한 패턴 감지
- `/root/.claude/projects/-root/memory/` 에 `feedback_*.md` 파일로 저장
- 이미 존재하는 유사 피드백이 있으면 카운트 증가

피드백 메모리 형식:
```markdown
---
name: feedback_[주제]
description: [한 줄 설명]
type: feedback
correction_count: [횟수]
first_seen: [날짜]
last_seen: [날짜]
---

[규칙 내용]

**Why:** [사용자가 교정한 이유]
**How to apply:** [적용 방법]
```

### 2. 패턴 승격 (`/self-improve 승격`)

`correction_count >= 3`인 피드백을 영구 규칙으로 승격한다.

1. `/root/.claude/projects/-root/memory/feedback_*.md` 파일 전체 스캔
2. `correction_count >= 3`인 항목 필터링
3. 해당 규칙을 CLAUDE.md 또는 MEMORY.md에 영구 반영
4. 승격된 피드백의 상태를 `promoted: true`로 업데이트

### 3. 목록 (`/self-improve 목록`)

현재 기록된 모든 교정 피드백을 테이블로 출력한다.

```
| # | 주제 | 횟수 | 최초 | 최근 | 승격 여부 |
|---|------|------|------|------|----------|
```

## 핵심 원칙

- **관찰**: 사용자가 "아니", "그거 말고", "이렇게 해" 등으로 교정할 때 감지
- **기록**: 맥락과 함께 저장 (왜 교정했는지, 어떤 상황에서)
- **승격**: 3회 반복 → 영구 규칙. 우연이 아닌 패턴만 승격
- **적용**: 승격된 규칙은 이후 모든 대화에서 자동 적용
