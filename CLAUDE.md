# Claude ワークスペースコンテキスト

## オーナー情報
- 名前：陣内 聡（株式会社ゆめ看護）
- GitHub：sjinnouchi-ux
- メール：s.jinnouchi@yumekango.com

## このリポジトリの目的
複数プロジェクトを1つのワークスペースで管理する。各プロジェクトはサブフォルダで独立している。

## 起動時の読み取り順序（重要）

**起動時はまず `INDEX.json` を読むこと。** その内容に従って、必要なプロジェクトの主要MDだけを後追いで読む。

1. `INDEX.json` を読む（全プロジェクトのowner・主要MDパス・最終更新日）
2. ユーザーから指示があったプロジェクトの `primary_docs` を読む
3. 必要に応じて該当プロジェクトの他のMDを追加で読む

`INDEX.json` の `projects.<name>.claude_read_only` が `true` のプロジェクト（Kアラート、Codex、yumekango-worker など）は **Claude は編集してはならない（読取専用）**。これらは Codex 担当領域である。

## プロジェクト一覧

詳細は `INDEX.json` を参照。owner と最新更新日も `INDEX.json` で確認できる。

| フォルダ | 概要 | owner |
|---------|------|-------|
| `market-pilot/` | 株式分析・LINE通知 | claude |
| `dori-manga/` | どり看護師 Instagram 漫画化 | claude |
| `code-exchange/` | Desktop ↔ CLI コード交換 | both |
| `codex/` | Codex 専用作業ルール | codex（Claude読取専用） |
| `k-alert-test/` | 公式LINE AI連携・Kアラート | codex（Claude読取専用） |
| `api-monitor/` | API利用費用の可視化ダッシュボード | claude |
| `company-settings/` | GA4・Google Ads 設定 | claude |
| `taiwan-outreach/` | 台湾向けインバウンド施策 | claude |
| `yumekango-worker/` | Cloudflare Worker（家計簿LIFF等） | codex（Claude読取専用） |

## 運用ルール（重要）

**Desktop（Claude Cowork）は GitHub Web UI（GitHub MCP含む）のみで操作する。**
- ローカルファイル書き込み（Writeツール）は使用しない
- すべてのファイル作成・編集は GitHub Web UI または GitHub MCP 経由で Commit する
- CLI は起動時に `INDEX.json` を読んで最新変更を把握する

**`claude_log.md` のアーカイブルール（月次）**
- ルート `claude_log.md` は直近1ヶ月のみ
- それ以前は `docs/archive/claude_log_YYYY-MM.md` へ移動する
- 翌月初に前月分をアーカイブへ退避する運用

## CLI起動時の作業フロー

1. `INDEX.json` で全体構造を把握
2. 対象プロジェクトの `primary_docs`（`CLAUDE.md` と `docs/work_log.md`）を読む
3. 作業実施
4. 対象プロジェクトの `docs/work_log.md` に記録
5. `git push` まで完結させる（push 後、GitHub Actions が `INDEX.json` の `last_updated` を自動更新）

## Claude Desktop からのコード受け取り

`code-exchange/` フォルダを使う。詳細は `code-exchange/README.md` を参照。

```bash
# 実行待ちコード確認
python code-exchange/manage.py list

# 完成報告（JSONを削除してpush）
python code-exchange/manage.py complete <id>
```

## Git運用

- リモート: `https://github.com/sjinnouchi-ux/workspace`
- 作業後は必ず `git push` まで完結させる
- `git pull` は Claude Code が随時実施する
- `INDEX.json` の `last_updated` は手動で書き換えない（Actionsが自動更新する）

## 環境

- Python: `/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- ローカルパス: `/Users/satoshijinnouchi/sjinnouchi-ux-workspace/`
