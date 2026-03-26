# /security-scan — Luxon 보안 스캔

전체 인프라 보안 취약점 스캔. 네트워크 노출, 인증 우회, 자격증명 유출 체크.

## 실행 순서

### 1. 포트 노출 체크
```bash
ss -tlnp | grep -v '127.0.0.1' | grep -v '::1'
```
- `0.0.0.0` 바인딩된 서비스가 인증 없이 열려있으면 **CRITICAL**
- 허용: 22(SSH), 80(nginx+auth), 443(TLS), 51820(WireGuard)
- 차단 필요: 8000, 8100, 11434, 12393, 18789-18803

### 2. UFW 방화벽 상태
```bash
ufw status verbose
```
- Default: deny incoming 확인
- 불필요한 ALLOW 규칙 없는지 확인

### 3. nginx 인증 우회 체크
```bash
ls /etc/nginx/sites-enabled/
nginx -T 2>/dev/null | grep -E '(auth_basic|proxy_pass|server_name)'
```
- 모든 proxy_pass가 auth_basic 블록 내부인지 확인
- server_name이 IP 직접접근 허용하는 별도 블록 없는지 확인

### 4. 자격증명 유출 체크
```bash
grep -r 'password\|secret\|api_key\|token' /etc/nginx/ --include='*.conf' 2>/dev/null
grep -rn 'Luxon2026\|htpasswd' /etc/nginx/ 2>/dev/null
```
- nginx 설정 파일 주석에 비밀번호 노출 여부

### 5. .env 파일 권한
```bash
ls -la /root/nexus-finance-mcp/.env /root/scripts/.env 2>/dev/null
ls -la /root/.claude/.credentials.json 2>/dev/null
```
- 600(owner only) 권한인지 확인
- 그 외 사용자 읽기 가능하면 **WARNING**

### 6. OpenClaw 게이트웨이 localhost 체크
```bash
ss -tlnp | grep openclaw
```
- 모든 게이트웨이가 127.0.0.1에만 바인딩인지 확인

### 7. MCP 서버 인증
```bash
curl -s --max-time 3 http://127.0.0.1:8100/health
curl -s --max-time 3 http://localhost:80/api/mcp/ 2>/dev/null | head -c 100
```
- 내부: health OK
- 외부: nginx basic auth 필요

## 출력 형식

| 항목 | 상태 | 설명 |
|------|------|------|
| 포트 노출 | OK/WARN/CRITICAL | 0.0.0.0 바인딩 현황 |
| UFW | OK/WARN | 방화벽 상태 |
| nginx 인증 | OK/CRITICAL | 우회 경로 여부 |
| 자격증명 | OK/WARN | 노출된 비밀 |
| 파일 권한 | OK/WARN | .env 파일 권한 |
| 게이트웨이 | OK/WARN | localhost 바인딩 |
| MCP 인증 | OK/CRITICAL | 외부 접근 차단 |

발견된 이슈는 즉시 수정 방안과 함께 보고.
