---
name: Vault 고립 노드 연결 작업
description: 옵시디언 그래프 뷰에서 노란색 고립 노드(에이전트 채팅/메모리)들을 MOC/허브에 wikilink로 연결 필요
type: project
---

옵시디언 그래프 뷰에서 노란색 점(에이전트 채팅 로그, 메모리 파일 등)이 대량으로 고립되어 있음. wikilink가 없어서 그래프에서 연결 안 됨.

**Why:** Vault가 지식 네트워크로 기능하려면 노드 간 연결이 필요. 고립 노트 = 죽은 지식.

**How to apply:**
- 고립 노드 스캔 스크립트 개발 (frontmatter tags + 파일명 패턴으로 분류)
- 에이전트별 MOC 노트 생성 (hermes-moc.md, oracle-moc.md 등)
- 각 고립 노트에 관련 MOC wikilink 자동 삽입
- 일일 메모리 파일들을 날짜별/주제별 허브에 연결
- 크론으로 주기적 고립 노드 정리 자동화 검토
