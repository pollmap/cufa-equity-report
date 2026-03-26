# /cron-health — 크론 작업 상태 체크

모든 크론 작업의 실행 여부와 출력 데이터 신선도 확인.

## 실행 순서

### 1. 크론 목록 확인
```bash
crontab -l
```

### 2. 데이터 파일 신선도 체크

| 파일 | 갱신 주기 | 경로 |
|------|----------|------|
| status.json | 1분 | /var/www/html/data/status.json |
| market-cache.json | 5분 | /var/www/html/data/market-cache.json |
| polymarket-cache.json | 5분 | /var/www/html/data/polymarket-cache.json |
| wallet-cache.json | 5분 | /var/www/html/data/wallet-cache.json |
| vault-stats.json | 5분 | /var/www/html/data/vault-stats.json |
| research-feed.json | 5분 | /var/www/html/data/research-feed.json |
| wsl-health.json | 5분 | /var/www/html/data/wsl-health.json |

```bash
for f in status market-cache polymarket-cache wallet-cache vault-stats research-feed wsl-health; do
  file="/var/www/html/data/${f}.json"
  if [ -f "$file" ]; then
    age=$(( $(date +%s) - $(stat -c %Y "$file") ))
    ts=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('timestamp','?'))" 2>/dev/null)
    err=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('error',''))" 2>/dev/null)
    echo "$f: age=${age}s ts=$ts err=$err"
  else
    echo "$f: MISSING"
  fi
done
```

### 3. 신선도 판정
- 1분 주기: 120초 이상 → STALE
- 5분 주기: 600초 이상 → STALE
- 6시간 주기: 25200초 이상 → STALE
- error 필드 존재 → DEGRADED

### 4. 크론 로그 확인
```bash
tail -5 /root/scripts/mcp-cache.log 2>/dev/null
tail -5 /root/scripts/dashboard-data.log 2>/dev/null
tail -5 /root/obsidian-vault/scripts/sync.log 2>/dev/null
```

### 5. flock 충돌 체크
```bash
ls -la /tmp/agent-status.lock 2>/dev/null
lsof /tmp/agent-status.lock 2>/dev/null
```

## 출력 형식

| 데이터 | 나이(초) | 상태 | 마지막 갱신 | 에러 |
|--------|---------|------|------------|------|
| status | 45s | FRESH | 21:46:02Z | - |
| market-cache | 180s | FRESH | 21:43:01Z | - |
| polymarket-cache | 720s | STALE | 21:33:01Z | API unavailable |
| ... | ... | ... | ... | ... |

STALE/DEGRADED 항목은 원인 분석 + 크론 수동 실행으로 즉시 복구.
