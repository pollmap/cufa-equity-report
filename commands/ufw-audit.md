---
description: "방화벽 + 포트 보안 감사 — UFW 상태, 0.0.0.0 바인딩 점검, 미인가 포트 탐지"
---

# UFW Audit

방화벽 상태와 네트워크 보안을 점검한다.

## 절차

1. UFW 상태 확인:
```bash
ufw status numbered
```

2. 0.0.0.0 바인딩 (외부 노출) 포트 스캔:
```bash
ss -tlnp | grep "0.0.0.0" | grep -v "127.0.0.1"
```

3. 허용된 포트만 열려있는지 확인:
   - 22/tcp (SSH) ✓
   - 80/tcp (nginx) ✓
   - 443/tcp (HTTPS) ✓
   - 51820/udp (WireGuard) ✓
   - 그 외 → 🔴 ALERT

4. 내부 전용 포트 확인 (127.0.0.1만):
   - 18789/18790/18800 (OpenClaw gateways)
   - 11434 (어댑터)
   - 12393 (아바타)

5. 미인가 포트 발견 시:
```bash
kill $(lsof -ti:{port}) 2>/dev/null
```

6. .env 파일 노출 확인:
```bash
find /root -maxdepth 3 -name ".env" -exec echo "⚠ {}" \;
```
