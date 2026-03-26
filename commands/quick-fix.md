# /quick-fix — 빠른 코드 수정 사이클

읽기→수정→재시작→검증 원샷 워크플로우. 작은 버그 수정이나 설정 변경에 사용.

## 사용법
```
/quick-fix [설명]
```

## 워크플로우

### 1. 문제 파악
- 에러 로그 또는 사용자 설명에서 원인 파일 특정
- 관련 파일 즉시 읽기 (Read)

### 2. 수정 적용
- Edit 도구로 최소 변경
- 변경 전후 diff 확인

### 3. 영향 범위 체크
- 변경된 함수/클래스를 import하는 파일 grep
- 사이드이펙트 없는지 확인

### 4. 서비스 재시작
해당 서비스만 재시작:
```bash
# 어떤 서비스에 영향?
# nexus-finance-mcp/ 아래 → systemctl restart nexus-finance-mcp (20초 대기)
# luxon-mcp/ 아래 → systemctl restart luxon-mcp-http
# openclaw 설정 → systemctl restart openclaw-[agent]
# nginx 설정 → nginx -t && systemctl reload nginx
# scripts/ 아래 → 크론이 자동 실행 (수동: python3 script.py)
```

### 5. 즉시 검증
```bash
# MCP health
curl -s http://127.0.0.1:8100/health | python3 -m json.tool

# 에러 로그 확인
journalctl -u [서비스] --no-pager -n 10 --since "1 min ago"
```

### 6. 결과 보고
```
[QUICK-FIX] 파일: path/to/file.py:줄번호
  문제: 설명
  수정: diff 요약
  검증: health OK / 에러 해소
```

## 주의사항
- MCP 서버 재시작은 26서버 로딩에 ~20초 소요
- nginx는 reload (restart 아님) 사용
- OpenClaw 에이전트는 진행 중인 세션 끊김 주의
