# /quality-gate — 커밋 전 품질 게이트

코드 변경사항에 대해 보안 + 품질 검사를 수행한다. 커밋 전 최종 확인용.

## 사용법
```
/quality-gate [파일경로...] [--strict]
```

인자 없으면 현재 staged + unstaged 변경사항 전체 검사.

## 검사 항목

### Gate 1: 시크릿 탐지 (14 패턴)

다음 패턴이 코드에 포함되면 **BLOCK**:

1. AWS Access Key (`AKIA[0-9A-Z]{16}`)
2. AWS Secret Key (`[0-9a-zA-Z/+]{40}`)
3. GitHub Token (`gh[pousr]_[A-Za-z0-9_]{36,}`)
4. Slack Token (`xox[baprs]-[0-9a-zA-Z-]+`)
5. Private Key (`-----BEGIN.*PRIVATE KEY-----`)
6. 일반 비밀번호 (`password\s*=\s*["'][^"']+["']`)
7. API Key 하드코딩 (`api[_-]?key\s*=\s*["'][^"']+["']`)
8. JWT Token (`eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+`)
9. Telegram Bot Token (`[0-9]{8,10}:AA[A-Za-z0-9_-]{33}`)
10. Discord Token (`[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27,}`)
11. .env 파일 커밋 시도
12. credentials/secret 파일 커밋 시도
13. DB 연결 문자열 (`(mysql|postgresql|mongodb)://[^"'\s]+`)
14. OpenAI API Key (`sk-[a-zA-Z0-9]{20,}`)

### Gate 2: 코드 품질

- **미사용 import** 감지 (Python: `import X` 후 X 미참조)
- **TODO/FIXME/HACK** 카운트 (경고)
- **print/console.log 디버그** 잔여 감지
- **하드코딩 IP/포트** 감지 (0.0.0.0 바인딩 경고)

### Gate 3: 보안 패턴

- **shell=True** 사용 (Python subprocess)
- **eval/exec** 사용
- **SQL 문자열 연결** (injection 위험)
- **innerHTML/dangerouslySetInnerHTML** 사용
- **CORS 와일드카드** (`Access-Control-Allow-Origin: *`)

### Gate 4: 설정 일관성

- systemd 서비스 수정 시 `daemon-reload` 필요 표시
- 환경변수 추가 시 `.env.example` 업데이트 확인
- 포트 변경 시 UFW/방화벽 규칙 확인 알림

## 출력 형식

```
╔══════════════════════════════════════╗
║         QUALITY GATE RESULT          ║
╠══════════════════════════════════════╣
║ Gate 1 (Secrets):  PASS / BLOCK     ║
║ Gate 2 (Quality):  PASS / WARN      ║
║ Gate 3 (Security): PASS / WARN      ║
║ Gate 4 (Config):   PASS / INFO      ║
╠══════════════════════════════════════╣
║ OVERALL:  ✓ CLEAR / ✗ BLOCKED      ║
╚══════════════════════════════════════╝
```

BLOCK이 하나라도 있으면 커밋 불가 권고.
WARN은 확인 후 진행 가능.

### --strict 모드
WARN도 BLOCK으로 처리. CI/CD 파이프라인용.
