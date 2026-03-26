---
description: "에이전트 SOUL.md 업데이트 — v3 역할에 맞게 SOUL.md 수정 후 재시작"
---

# SOUL.md Update

에이전트의 SOUL.md를 수정하고 안전하게 재시작한다.

## 입력
$ARGUMENTS: {에이전트이름} {수정내용 또는 "show"}

## SOUL.md 경로
- HERMES: `/root/hermes-home/.openclaw/workspace/SOUL.md`
- NEXUS: `/root/nexus-home/.openclaw/workspace/SOUL.md`
- ORACLE: `/root/oracle-home/.openclaw/workspace/SOUL.md`
- MERCHANT: `/root/hermes-home/.openclaw/workspace-merchant/SOUL.md`
- TREASURER: `/root/hermes-home/.openclaw/workspace-treasurer/SOUL.md`
- PROPHET: `/root/oracle-home/.openclaw/workspace-prophet/SOUL.md`
- VOYAGER: `/root/nexus-home/.openclaw/workspace-voyager/SOUL.md`

## 절차

1. 현재 SOUL.md 읽기
2. 수정사항 적용 (Edit 도구)
3. v3 역할과 일관성 확인:
   - HERMES (ESTP): 트레이딩+ACP+수익
   - NEXUS (ENFJ): 동아리/팀 공유
   - ORACLE (INTJ): 개인비서+퀀트+롤플
4. Vault 저장 규칙 섹션 유지 확인
5. 에이전트 재시작

## v3 MBTI 성격 매트릭스
| 에이전트 | MBTI | 핵심 | 톤 |
|---------|------|------|-----|
| HERMES | ESTP | 빠른 판단, 기회 포착 | 밝고 민첩, 존댓말 |
| NEXUS | ENFJ | 교육, 팀 빌딩 | 부드럽고 정중 |
| ORACLE | INTJ | 정밀, 전략 | 차분, 확률로 말함 |
