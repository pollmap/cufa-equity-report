---
name: 외부 프로젝트 참고 자료 (2026.04.05)
description: Karpathy Wiki, OpenClaude, Obsidian Mind, DeepScientist, Anthropic Harness — Luxon AaaS 설계 참고
type: reference
---

# 외부 프로젝트 참고 (2026.04.05 찬희 공유)

## 1. Karpathy LLM 지식 기반
- raw/ → wiki/ → outputs/ 구조, LLM이 위키 자동 컴파일
- Obsidian을 프론트엔드로 사용
- 누적 학습 루프: 쿼리 결과를 위키에 재저장
- 우리 적용: Vault + MCP 데이터 수집 + 결과 자동 저장

## 2. OpenClaude (gitlawb.com/node/repos/z6MkqDnb/openclaude)
- Claude Code를 멀티 LLM(200+모델)으로 확장한 오픈소스 포크
- agentRouting: 에이전트별 모델 라우팅 (비용 최적화)
- .openclaude-profile.json 프로바이더 프로파일
- 참고: 에이전트 라우팅 패턴, 프로바이더 추상화

## 3. Obsidian Mind (github.com/breferrari/obsidian-mind)
- Claude Code의 장기 기억을 Obsidian Vault로 구현
- 15개 슬래시 커맨드 + 9개 서브에이전트
- /standup, /weekly, /incident-capture 자동화
- 우리 적용: 이미 유사 구조 (Vault 70+ 노트, MCP vault_* 도구)

## 4. DeepScientist (github.com/ResearAI/DeepScientist)
- 로컬에서 작동하는 AI 연구 스튜디오
- 자동 지식 생성 + 연결

## 5. Anthropic Harness Design
- "만드는 놈(Generator) ≠ 평가하는 놈(Evaluator)" 원칙
- context fork로 평가 격리
- 임계값 설정 (3.5/5 미만 → 자체 수정)
- 우리 적용: 3-에이전트 코드 가드 (이미 CLAUDE.md에 있음)

## 6. Acemoglu 지식 붕괴 논문 (MIT, 2026.02.20)
- AI가 너무 정확하면 인간 학습 중단 → 집단 지식 붕괴
- 비단조 복지 곡선: 적당한 AI=이득, 과도한 AI=재앙
- 우리 대응: "LLM ≠ trader", Kill Conditions, 출처 명시

## 7. Day1Global Skills (github.com/star23/Day1Global-Skills)
- 에이전트 스킬 컬렉션
