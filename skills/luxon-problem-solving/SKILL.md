---
name: luxon-problem-solving
description: "Luxon/찬희 검증된 문제해결 패턴 모음. audit→fix, 12-point review, 병렬 탐색, 보안 우선, 테이블 정리. 트리거: '문제 해결', '디버그', '왜 안 돼', '오류', '점검', '감사'."
---

# Luxon 문제해결 패턴 스킬

## 1. 핵심 철학

**"먼저 보고, 고치고, 검증한다"** (audit → fix → verify)
추측하지 말고 실측하라. 로그 > 가설.

## 2. 패턴 A: Audit → Fix (인프라 문제)

```
1. 현재 상태 스냅샷 (서비스/포트/로그/메모리)
2. 기대값과 비교 (뭐가 달라?)
3. 원인 특정 (로그에서 에러 패턴 찾기)
4. 최소 변경으로 수정
5. 재시작 + 검증
6. 결과 테이블로 정리
```

**실전 예시** (오늘 적용):
- MCP 8100 "Not Found" → nohup.out에서 ClosedResourceError 발견 → SSE→streamable-http 전환
- WSL "inactive" → SSH 경유 확인하니 실제로 active → 모니터링 방법 수정

## 3. 패턴 B: 12-Point Deep Review (코드 변경)

모든 코드 변경 후 12개 항목 체크:

| # | 항목 | 질문 |
|---|------|------|
| 1 | 목적 부합 | 원래 의도대로 동작? |
| 2 | 버그 | null 체크, off-by-one, 타입 불일치? |
| 3 | 보안 | 입력 검증, 인증, 정보 노출? |
| 4 | 크기 | 함수 100줄, 파일 500줄 초과? |
| 5 | 재사용 | 기존 유틸리티 활용? |
| 6 | 사이드이펙트 | 글로벌 상태, 파일쓰기, 스레드? |
| 7 | 일관성 | 네이밍, 에러 형식, 로깅 레벨? |
| 8 | 정리 | 사용 안 하는 import/변수? |
| 9 | 품질 | 타입힌트, 매직넘버? |
| 10 | UX | 에러 메시지 유용? 타임아웃? |
| 11 | 연관 | 호출하는 곳 전부 확인? |
| 12 | 배포 | systemd 재시작? 환경변수? 롤백? |

## 4. 패턴 C: 병렬 탐색 (모르는 문제)

```
문제 불명확할 때:
  → Agent 3개 동시 발사 (Explore subagent)
  → 각각 다른 각도로 탐색
  → 결과 머지 → 전체 그림 파악

예: MCP 오류 원인 모를 때
  Agent 1: 서비스 상태 + 포트 + 프로세스
  Agent 2: MCP 설정 + 코드 + 로그
  Agent 3: OpenClaw + 통합 포인트
```

## 5. 패턴 D: 보안 우선 (변경 시)

```
모든 네트워크 변경 전:
1. 현재 바인딩 확인 (ss -tlnp)
2. UFW 상태 확인
3. 변경 후 외부 접근 테스트
4. 인증 경로 확인 (nginx auth)

보안 체크리스트:
- [ ] 0.0.0.0 바인딩 없음 (22/80 제외)
- [ ] .env 파일 600 권한
- [ ] 에러 메시지에 내부 경로 미포함
- [ ] subprocess에 shell=True 없음
- [ ] 사용자 입력 검증 (길이, 형식)
```

## 6. 패턴 E: 빠른 수정 사이클

```
읽기 (Read) → 수정 (Edit) → 재시작 → 검증 (curl/systemctl)
  └─ 30초 이내 완료 목표
  └─ MCP는 20초 대기 (26서버 로딩)
  └─ nginx는 reload (restart 아님)
```

## 7. 출력 규칙

- **항상 테이블로 정리** (마크다운 테이블)
- **PASS/WARN/FAIL** 3단계 판정
- **FAIL은 즉시 수정 코드와 함께**
- **수치는 실측값** (추측 금지)

## 8. 자주 쓰는 진단 명령어

```bash
# 서비스 상태
systemctl is-active [서비스]

# 포트 바인딩
ss -tlnp | grep [포트]

# MCP 건강
curl -s http://127.0.0.1:8100/health

# 에러 로그
journalctl -u [서비스] --since "1 hour ago" -p err

# WSL 접속
ssh valuealpha@10.0.0.2 "[명령어]"

# Vault 상태
cd /root/obsidian-vault && git status
```
