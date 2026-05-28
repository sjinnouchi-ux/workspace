# workspace

陣内 聡（株式会社ゆめ看護）の開発ワークスペースです。  
**Claude Desktop・Claude Code CLI 共通の起動時読み込みファイルです。**

---

## プロジェクト一覧

| フォルダ | 概要 |
|---------|------|
| [market-pilot](./market-pilot/) | 株式市場分析・売買シグナル・LINE自動通知システム |
| [code-exchange](./code-exchange/) | Claude Desktop ↔ CLI 間のコードやり取り |
| [dori-manga](./dori-manga/) | どり看護師 Instagram 漫画化プロジェクト |
| [codex](./codex/) | Codex専用の作業ルール・GASブラウザ操作運用 |

---

## 運用ルール

### Claude Desktop（Cowork）
- **GitHub Web UI のみで操作**（ローカルへの直接書き込みは行わない）
- ファイル操作後は必ずこの README.md の「Desktop作業ログ」を更新する
- code-exchange に渡すコードは `.md` + `.json` をセットで作成する

### Claude Code CLI
- 起動時に `git pull` → この README.md を読んで最新状況を把握する
- code-exchange の pending を確認して実行する
- 作業後は `docs/work_log.md` と `claude_log.md` に記録して `git push`

---

## code-exchange の使い方

```
code-exchange/
├── exchanges/
│   ├── YYYYMMDD-NNN.md    ← コード本体（完了後も残す）
│   └── YYYYMMDD-NNN.json  ← 実行待ちフラグ（完了時に削除）
└── manage.py
```

**JSONあり = pending（実行待ち） / JSONなし = 完了済み**

```bash
git pull
python code-exchange/manage.py list           # 実行待ち一覧
python code-exchange/manage.py show <id>      # 内容確認
python code-exchange/manage.py complete <id>  # 完了処理
```

### スクリプト種別ごとの実行コマンド

| 種別 | .json の `"type"` | CLIコマンド |
|------|-------------------|------------|
| **Python** | `"python"` | `cd ~/sjinnouchi-ux-workspace && python3 code-exchange/exchanges/YYYYMMDD-NNN.py && python3 code-exchange/manage.py complete YYYYMMDD-NNN` |
| **GAS** | `"gas"` | `cd ~/sjinnouchi-ux-workspace && cd <project_dir> && clasp push && clasp run <function> && cd ~/sjinnouchi-ux-workspace && python3 code-exchange/manage.py complete YYYYMMDD-NNN` |

**GAS の .json には以下フィールドを追加：**
```json
{
  "type": "gas",
  "project_dir": "dori-manga/gas/clasp-project",
  "function": "run"
}
```

> ⚠️ `clasp run` は Google Cloud OAuth の初回セットアップが必要（未完了・別途実施予定）

---

## Desktop作業ログ

> CLIが `git pull` 後にここを確認することで、Desktopの最新作業を把握できます。
> 📋 詳細: https://github.com/sjinnouchi-ux/workspace/commits/main

| 日付 | 作業内容 | 対象 |
|------|----------|------|
| 2026-05-28 | Codex専用フォルダ・GASブラウザ操作運用メモ追加 | `codex/`, `README.md` |
| 2026-05-27 | GASワークフロールール追加（clasp run方式）| `README.md` |
| 2026-05-27 | どり漫画管理フォルダ作成GASスクリプト追加 | `dori-manga/gas/` |
| 2026-05-19 | dori-manga プロジェクトフォルダ作成 | `dori-manga/` |
| 2026-05-19 | code-exchange 疎通確認テスト投入 | `code-exchange/exchanges/20260519-001` |
| 2026-05-19 | README運用ルール・Desktop作業ログ追加 | `README.md`, `CLAUDE.md` |

---

## 作業フロー

1. **起動時にこの README.md を読む**（Desktop作業ログで最新変更を確認）
2. 対象プロジェクトの `CLAUDE.md` と `docs/work_log.md` を読む
3. 作業実施
4. `docs/work_log.md` と `claude_log.md` に記録 → `git push`

---

## 環境

- Python: 3.13.3（pyenv）`/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- clasp: インストール済み（GAS CLI実行ツール）
- GitHub: https://github.com/sjinnouchi-ux/workspace
- ローカルパス: `/Users/satoshijinnouchi/sjinnouchi-ux-workspace/`
- GitHub認証: HTTPS + macOSキーチェーン
