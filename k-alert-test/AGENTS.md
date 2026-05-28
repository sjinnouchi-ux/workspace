# Kアラート・テスト開発 作業ルール

## 概要

公式LINE、Cloudflare Worker、GAS、スプレッドシート、AI API、ChatWork APIを連携するテスト開発プロジェクト。

## 守ること

- 既存の家計簿LIFF/GAS/スプレッドシートを壊さない
- 既存のmarket-pilot LINE通知を壊さない
- 本番Webhook変更前に必ずテスト手順を確認する
- 秘密情報はMarkdownやコードに直書きしない
- GASでは `PropertiesService.getScriptProperties()` を使う
- Workerでは `wrangler secret` を使う
- 作業後は `docs/work_log.md` とルート `claude_log.md` に記録する

## 主要ファイル

- `docs/sheet_schema.md`: スプレッドシート設計
- `docs/implementation_plan.md`: 実装計画
- `docs/manual_setup.md`: Google/LINE/Cloudflareの手動設定手順
- `gas/Code.gs`: Kアラート用GAS雛形
- `worker/worker.js`: Cloudflare Workerルーティング雛形

