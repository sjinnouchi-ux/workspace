# workspace

陣内 聡（株式会社ゆめ看護）の開発ワークスペースです。  
**Claude Desktop・Claude Code CLI 共通の起動時読み込みファイルです。**

---

## プロジェクト一覧

| フォルダ | 概要 |
|---------|------|
| [market-pilot](./market-pilot/) | 株式市場分析・売買シグナル・LINE自動通知システム |
| [code-exchange](./code-exchange/) | Claude Desktop ↔ CLI 間のコードやり取り |

---

## code-exchange の使い方

Claude Desktop でコードを生成し、Claude Code CLI で実行するための仕組みです。

### ファイル構成

```
code-exchange/
├── exchanges/
│   ├── YYYYMMDD-NNN.md    ← コード本体・説明（完了後も残す）
│   └── YYYYMMDD-NNN.json  ← 実行待ちを示すメタデータ（完了時に削除）
└── manage.py              ← 管理スクリプト
```

**JSONファイルが存在する = 実行待ち（pending）**  
**JSONファイルがない = 完了済み**

### Claude Desktop 側の手順

1. `code-exchange/exchanges/template.md` をコピーして新しいファイルを作成
2. ファイル名は `YYYYMMDD-NNN.md`（例: `20260519-001.md`）
3. コードと説明を記入
4. 同名の `.json` ファイルを以下の形式で作成：
   ```json
   {
     "id": "20260519-001",
     "title": "タスクのタイトル",
     "status": "pending",
     "created": "20260519",
     "md_file": "20260519-001.md"
   }
   ```
5. GitHubにpush（`git add` → `git commit` → `git push`）

### Claude Code CLI 側の手順

```bash
# 最新を取得
git pull

# 実行待ち一覧を確認
python code-exchange/manage.py list

# 内容を確認
python code-exchange/manage.py show 20260519-001

# 実行後、完成報告（JSONを削除してpush）
python code-exchange/manage.py complete 20260519-001
```

---

## 作業フロー（共通）

1. **起動時にこの README.md を読む**
2. 対象プロジェクトの `CLAUDE.md` と `docs/work_log.md` を読んでコンテキストを把握
3. 作業実施
4. `docs/work_log.md` と `claude_log.md` に記録 → `git push`

---

## 環境

- OS: macOS（常時起動）
- Python: 3.13.3（pyenv）`/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- GitHub: https://github.com/sjinnouchi-ux/workspace
- ローカルパス: `/Users/satoshijinnouchi/sjinnouchi-ux-workspace/`
- GitHub認証: HTTPS + macOSキーチェーン
