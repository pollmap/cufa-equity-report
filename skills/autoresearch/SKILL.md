# Autoresearch Skill

> Karpathy 방법론 기반 — 스킬 자동 개선 루프

## 설명

이 스킬은 다른 스킬의 품질을 자동으로 개선한다.
체크리스트 기반 pass/fail 평가 → 작은 변경 → 재평가 → 개선 유지/복원.

## 트리거

사용자가 "autoresearch [스킬명]" 또는 "스킬 개선해줘" 라고 하면 실행.

## 프로세스

### Phase 1: 베이스라인 측정

1. 대상 스킬의 SKILL.md 읽기
2. 체크리스트 정의 (3-6개 yes/no 질문)
   - 사용자와 함께 정의하거나 자동 생성
3. 대상 스킬을 5회 실행 (테스트 입력 사용)
4. 각 출력을 체크리스트로 평가
5. 베이스라인 pass rate 기록 (예: 56%)

### Phase 2: 반복 개선 루프

```
REPEAT:
  1. 현재 가장 낮은 pass rate 질문 식별
  2. SKILL.md에 작은 변경 1개 적용
     - 규칙 추가, 예시 추가, 제약 강화 등
  3. 수정된 스킬을 5회 재실행
  4. 새 pass rate 측정
  5. IF 개선됨 → 변경 유지
     ELSE → 변경 복원
  6. 변경 로그 기록
UNTIL pass_rate >= 95% (3회 연속) OR max_rounds 도달
```

### Phase 3: 결과 보고

- 최종 pass rate
- 변경 로그 (무엇을 시도했고, 무엇이 효과 있었는지)
- 원본 SKILL.md 백업
- 개선된 SKILL.md

## 체크리스트 예시

```
Landing Page Copy Skill:
☐ 헤드라인에 구체적 숫자/결과 포함?
☐ 버즈워드(revolutionary, cutting-edge) 없음?
☐ CTA에 구체적 동사 사용?
☐ 첫 문장에 구체적 페인포인트 언급?
☐ 전체 150단어 이내?
```

## 적용 가능 대상

- NEXUS IC-Prep 스킬
- HERMES ACP 서비스 품질
- DOGE 리서치 카드 생성 (향후)
- 모든 SOUL.md 프롬프트 개선
