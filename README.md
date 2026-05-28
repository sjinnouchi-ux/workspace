# workspace

陣内 聡（株式会社ゆめ看護）の開発ワークスペースです。  
**Claude Desktop・Claude Code CLI 共通の起動時読み込みリポジトリです。**

---

## 起動時の読み取り順序（必読）

1. **`INDEX.json` を読む** ← 起動時の最初のステップ。全プロジェクトのowner・主要MDパス・最終更新日が集約されている
2. 対象プロジェクトの `primary_docs`（多くは `CLAUDE.md` と `docs/work_log.md`）を読む
3. 必要に応じて該当プロジェクトの他のMDを追加で読む

> `INDEX.json.projects.<name>.claude_read_only` が `true` のプロジェクトは Claude 読取専用（Codex 担当）。Claude は編集してはならない。

---

## プロジェクト一覧

詳細・最新更新日は `INDEX.json` を参照。

| フォルダ | 概要 | owner |
|---------|------|-------|
| [market-pilot](./market-pilot/) | 株式市場分析・売買シグナル・LINE自動通知 | claude |
| [dori-manga](./dori-manga/) | どり看護師 Instagram 漫画化 | claude |
| [code-exchange](./code-exchange/) | Claude Desktop ↔ CLI 間のコード交換 | both |
| [codex](./codex/) | Codex 専用作業ルール・GASブラウザ運用 | codex（Claude読取専用） |
| [k-alert-test](./k-alert-test/) | 公式LINE AI連携・Kアラート | codex（Claude読取専用） |
| [api-monitor](./api-monitor/) | API利用費用の可視化ダッシュボード | claude |
| [company-settings](./company-settings/) | GA4・Google Ads 設定 | claude |
| [taiwan-outreach](./taiwan-outreach/) | 台湾向けインバウンド施策 | claude |
| [yumekango-worker](./yumekango-worker/) | Cloudflare Worker（家計簿LIFF等） | codex（Claude読取専用） |

---

## 運用ルール

### Claude Desktop（Cowork）
- **GitHub Web UI / GitHub MCP のみで操作**（ローカルへの直接書き込みは行わない）
- `claude_read_only: true` のプロジェクトは編集しない
- code-exchange に渡すコードは `.md` + `.json` をセットで作成する

### Claude Code CLI
- 起動時に `git pull` → `INDEX.json` を読んで最新状況を把握する
- code-exchange の pending を確認して実行する
- 作業後は `docs/work_log.md` と `claude_log.md` に記録して `git push`
- push 後、GitHub Actions が `INDEX.json` の `last_updated` を自動更新する

### claude_log.md のアーカイブ運用（月次）
- ルート `claude_log.md` は **直近1ヶ月のみ**
- それ以前は `docs/archive/claude_log_YYYY-MM.md` へ移動
- 翌月初に前月分をアーカイブへ退避する

### INDEX.json の更新
- `last_updated` は **GitHub Actions が自動更新**（`.github/workflows/update-index.yml`）
- プロジェクト追加・削除・owner変更などの構造変更は手動で `INDEX.json` を編集
- 手動編集時は `paths-ignore: INDEX.json` によりActionsは発火しない

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

> 直近の主要変更は `INDEX.json` の `last_updated` と GitHub の commit 履歴で把握できます。
> 📋 commit履歴: https://github.com/sjinnouchi-ux/workspace/commits/main

| 日付 | 作業内容 | 対象 |
|------|----------|------|
| 2026-05-28 | INDEX.json導入・自動更新ワークフロー追加 | `INDEX.json`, `.github/` |
| 2026-05-28 | Kアラート・テスト開発プロジェクト初期化 | `k-alert-test/`, `README.md` |
| 2026-05-28 | Codex専用フォルダ・GASブラウザ操作運用メモ追加 | `codex/`, `README.md` |
| 2026-05-27 | GASワークフロールール追加（clasp run方式）| `README.md` |
| 2026-05-27 | どり漫画管理フォルダ作成GASスクリプト追加 | `dori-manga/gas/` |
| 2026-05-19 | dori-manga プロジェクトフォルダ作成 | `dori-manga/` |
| 2026-05-19 | code-exchange 疎通確認テスト投入 | `code-exchange/exchanges/20260519-001` |
| 2026-05-19 | README運用ルール・Desktop作業ログ追加 | `README.md`, `CLAUDE.md` |

---

## 環境

- Python: 3.13.3（pyenv）`/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- clasp: インストール済み（GAS CLI実行ツール）
- GitHub: https://github.com/sjinnouchi-ux/workspace
- ローカルパス: `/Users/satoshijinnouchi/sjinnouchi-ux-workspace/`
- GitHub認証: HTTPS + macOSキーチェーン
