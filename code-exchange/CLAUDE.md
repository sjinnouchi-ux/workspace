# Cowork運用ルール改善メモ（2026-05-26）

## 1. GitHub初動連携の扱い

### 現状の問題
CoworkはGitHubへの直接write接続が制限されており、初動でpushが失敗することがある。

### 確定運用フロー
1. **Cowork（Claude Desktop）** がローカルoutputsフォルダに `.md` / `.json` を生成
2. ユーザーがCLI（Claude Code）で以下を実行してコピー＆push：

```bash
# outputsフォルダからcode-exchangeへコピー
cp ~/Library/Application\ Support/Claude/local-agent-mode-sessions/*/outputs/YYYYMMDD-NNN.md \
   ~/sjinnouchi-ux-workspace/code-exchange/exchanges/
cp ~/Library/Application\ Support/Claude/local-agent-mode-sessions/*/outputs/YYYYMMDD-NNN.json \
   ~/sjinnouchi-ux-workspace/code-exchange/exchanges/

cd ~/sjinnouchi-ux-workspace
git add code-exchange/exchanges/YYYYMMDD-NNN.*
git commit -m "add exchange YYYYMMDD-NNN"
git push
```

---

## 2. Pythonスクリプト実行ルール（全作業で必須）

### 原則
**PythonスクリプトはすべてCLI（Claude Code）で実行する。Coworkから直接実行しない。**

### 理由
- Google OAuth認証はローカル環境にのみ保存されており、CLI環境からのみ利用可能
- code-exchangeシステムでの実行履歴・ログ管理を一元化するため

### Cowork側の出力フォーマット（省略不可・毎回必須）

Coworkがスクリプトを生成した場合は、必ず以下の3点をセットで出力する：

**① `YYYYMMDD-NNN.md`**（コード本体）
```markdown
# タイトル

## 概要
...

## 実行スクリプト

\```python
# コードをここに記載
\```
```

**② `YYYYMMDD-NNN.json`**（メタデータ）
```json
{
  "id": "YYYYMMDD-NNN",
  "title": "タイトル",
  "status": "pending",
  "created": "YYYY-MM-DDT00:00:00+09:00"
}
```

**③ CLI実行指示（一括コピペ可能な単一ブロック）**

```
cd ~/sjinnouchi-ux-workspace && git pull
python code-exchange/manage.py show YYYYMMDD-NNN > /tmp/taskX_raw.txt
python3 -c "
import re
with open('/tmp/taskX_raw.txt', 'r') as f:
    content = f.read()
match = re.search(r'\`\`\`python\n(.*?)\n\`\`\`', content, re.DOTALL)
if match:
    with open('script_name.py', 'w') as out:
        out.write(match.group(1))
    print('スクリプト抽出完了')
"
python3 script_name.py
python code-exchange/manage.py complete YYYYMMDD-NNN
```

---

## このファイルのコピー先

以下2か所に反映することを推奨：

1. **`~/sjinnouchi-ux-workspace/code-exchange/CLAUDE.md`** → CLIが起動時に読む
2. **jinnouchi-profileスキル `SKILL.md`** の「運用ルール」セクションに追記 → Coworkが次回から参照する
