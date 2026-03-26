---
description: "Vault Inbox 능동 발화 테스트 — 파일 생성→luxon_feed 감지→아바타 발화 확인"
---

# Vault Inbox Test

Obsidian Vault Inbox에 테스트 파일을 생성하여 luxon_feed.py 능동 발화 파이프라인을 검증.

## 절차

1. 대상 에이전트 결정 (hermes/nexus/oracle)
2. 테스트 파일 생성:
```bash
cat > /root/obsidian-vault/00-Inbox/{agent}/test-$(date +%s).md << 'EOF'
---
date: $(date +%Y-%m-%d)
agent: {agent}
tags: [test, feed]
---

능동 발화 테스트입니다. 이 메시지가 아바타에서 재생되면 파이프라인 정상.
EOF
```

3. luxon-feed 로그 확인:
```bash
journalctl -u luxon-feed --no-pager -n 5 --since "1 min ago"
```

4. 예상 결과:
   - `[{agent}] 새 파일 감지: test-*.md` 로그
   - WebSocket 전송 시도 (브라우저 클라이언트 연결 시 아바타 발화)

5. 테스트 파일 정리:
```bash
rm /root/obsidian-vault/00-Inbox/{agent}/test-*.md
```

## 주의
- 브라우저 클라이언트 없으면 WebSocket 500 에러 정상
- 쿨다운 60초 — 같은 에이전트 연속 테스트 시 스킵될 수 있음
