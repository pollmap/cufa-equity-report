---
name: project_luxon_avatar
description: Luxon Avatar - Open-LLM-VTuber with OpenClaw adapter, Live2D desktop pet for HERMES/NEXUS/ORACLE
type: project
---

Luxon Avatar = Open-LLM-VTuber v1.2.0+83 포크. VPS에서 Live2D 아바타 + 음성 대화.

**Why:** Luxon 에이전트에 시각적 존재감 부여 + 능동 발화(Morning Brief 등) + 데스크탑 펫

**How to apply:**
- 위치: `/root/luxon-avatar/Open-LLM-VTuber/`
- 어댑터: `/root/luxon-avatar/openclaw-adapter/adapter.py` (:11434)
- systemd: `luxon-avatar.service` (:12393), `luxon-adapter.service` (:11434)
- 접속: SSH 터널 `ssh -L 12393:localhost:12393` → 브라우저 localhost:12393
- 캐릭터: conf.yaml(HERMES 기본), characters/ko_nexus.yaml, characters/ko_oracle.yaml
- 전환: WebSocket `{"type": "switch-config", "file": "ko_nexus.yaml"}`
- MCP: stdio만 지원 (SSE 미지원). markitdown, time, ddg-search 등록
- 능동 발화: `ai-speak-signal` WebSocket 메시지 (Phase 3 미완)
- v3 캐릭터 YAML 적용 완료 (2026-03-22)
- 디스코드 전환: 찬희님 봇 생성 대기 중
