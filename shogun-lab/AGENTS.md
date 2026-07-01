# Shogun（仮） Project Rules

このフォルダは、Shogun設計MarkdownとCodex実行結果をつなぐための中継領域です。

## Source Of Truth

- Shogun設計MD: `handoffs/`
- Codex実行ログ: `codex-execution/`
- 運用ログ: `docs/work_log.md`
- セットアップ状態: `docs/setup_status.md`

## Required Startup

1. ルートの `PROJECTS.md` と `docs/workflow-design-implementation.md` を読む。
2. この `shogun-lab/AGENTS.md` を読む。
3. 実装対象が別プロジェクトの場合、そのプロジェクトの `AGENTS.md` と主要ドキュメントも読む。
4. `handoffs/` の対象MDを読み、実行範囲・検証条件・禁止事項を確認する。

## Handoff Rules

- Shogunが作ったMDをそのまま実行せず、Codexは対象リポジトリの現状を確認してから実行する。
- 未確認の月次レビュー、KPI、SNS/PR、意思決定ログ、進捗表は推測で埋めない。
- 実行対象が既存プロジェクトに属する場合、最終ログはこのフォルダだけでなく対象プロジェクト側にも残す。
- 外部サービス、デプロイ、ライブサイトに影響する作業は、repo state / editor or config state / deployed or live state を分けて報告する。
- 秘密情報は保存しない。必要な値は `C:\Users\irodo\.codex\.sandbox-secrets\global.env` から必要なキーだけ一時的に読む。

## Naming

- Shogun設計MD: `handoffs/YYYY-MM-DD-<topic>.md`
- Codex実行結果: `codex-execution/YYYY-MM-DD-<topic>-result.md`
- 迷った場合は、対象プロジェクト名を `<topic>` の先頭に入れる。
