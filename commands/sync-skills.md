# /sync-skills — 3개 환경 스킬/커맨드 동기화

스킬과 커맨드를 Windows/VPS/WSL 전체에 동기화합니다.

## 실행 순서

1. 현재 환경의 변경사항 커밋 + push:
```bash
cd ~/.claude && git add skills/ commands/ && git commit -m "sync: $(date +%Y%m%d-%H%M)" && GIT_SSH_COMMAND="ssh -i ~/.ssh/cbnupollmap -o BatchMode=yes" git push origin main
```

2. 다른 환경에서 pull:
```bash
# VPS
ssh -o BatchMode=yes -i ~/.ssh/cbnupollmap root@62.171.141.206 "cd /root/claude-skills-local && git pull origin main"

# WSL
wsl -- bash -c "cd ~/claude-skills-local && GIT_SSH_COMMAND='ssh -i ~/.ssh/cbnupollmap -o BatchMode=yes' git pull origin main"
```

3. 동기화 확인:
```bash
echo "Windows:" && ls ~/.claude/skills/ | wc -l
ssh -o BatchMode=yes -i ~/.ssh/cbnupollmap root@62.171.141.206 "echo 'VPS:' && ls /root/.claude/skills/ | wc -l"
wsl -- bash -c "echo 'WSL:' && ls ~/.claude/skills/ | wc -l"
```

## 참고
- VPS와 WSL은 symlink로 연결되어 있어서 pull만 하면 자동 반영
- OpenClaw 에이전트(HERMES/NEXUS/ORACLE)도 symlink로 연결됨
- 충돌 시: `git pull --rebase origin main`
