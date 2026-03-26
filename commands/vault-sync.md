# Vault Git 동기화

Obsidian Vault 변경사항을 GitHub에 동기화해.

## 실행

```bash
cd /root/obsidian-vault
git status
git add -A
git diff --cached --stat
```

변경사항이 있으면:
- 커밋 메시지는 변경된 파일/내용 기반으로 자동 작성
- `git push origin master`
- 결과 보고 (추가/수정/삭제 파일 수)

변경사항 없으면 "Vault clean, 동기화 불필요" 보고.
