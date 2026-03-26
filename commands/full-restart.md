---
description: "전체 Luxon 서비스 순차 재시작 — 모든 에이전트+인프라 안전하게 재시작"
---

# Full Restart

모든 Luxon 서비스를 안전한 순서로 재시작한다.

## 순서 (의존성 기반)

```bash
# 1. MCP 서버 먼저
systemctl restart nexus-finance-mcp
sleep 3

# 2. OpenClaw 에이전트 (NEXUS는 특수 처리)
systemctl restart openclaw-hermes
systemctl restart openclaw-oracle
sleep 3

# NEXUS: 포트 정리 후 시작
fuser -k 18790/tcp 2>/dev/null
sleep 2
systemctl restart openclaw-nexus
sleep 5

# 3. 어댑터 (에이전트 의존)
systemctl restart luxon-adapter
sleep 3

# 4. 아바타 (어댑터 의존)
systemctl restart luxon-avatar
sleep 3

# 5. 피드 (아바타 의존)
systemctl restart luxon-feed
sleep 2
```

## 검증

```bash
for svc in nexus-finance-mcp openclaw-hermes openclaw-nexus openclaw-oracle luxon-adapter luxon-avatar luxon-feed; do
  printf "%-25s %s\n" "$svc" "$(systemctl is-active $svc)"
done
```

## 포트 확인
```bash
for p in 8100 18789 18790 18800 11434 12393; do
  printf ":%s %s\n" "$p" "$(ss -tlnp | grep :$p | wc -l | xargs -I{} sh -c '[ {} -gt 0 ] && echo ✓ || echo ✗')"
done
```
