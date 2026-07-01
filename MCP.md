# MCP / 外部ツール / MiniPC 運用ルール

MCP、外部コネクタ、認証、MiniPC構築、バックアップの共通方針をここに集約する。

秘密値そのものは書かない。キー名、手順、再設定が必要な項目だけを書く。

## Common Rules

- Gitに入れてよいもの: ルーティング、非秘密設定、必要な環境変数名、セットアップ手順。
- Gitに入れてはいけないもの: APIキー、OAuth token、refresh token、GitHub token、Google認証情報、パスワード。
- APIキーは `config/settings.yaml` やMarkdownへ書かない。
- 実値はMiniPCローカルの非コミット `.env` や安全な秘密情報管理先で扱う。

## Codex Rules

- Codexは実装、検証、デプロイ、ローカルコマンド実行を担当する。
- 作業結果は各プロジェクトGitの `IMPLEMENTATION_LOG.md` に追記する。
- 設計と食い違う点は `Questions Back To Design` として返す。

## Claude / Shogun Rules

- Claude割当エージェントは要件定義、仕様整理、設計判断、レビューを担当する。
- 設計結果は各プロジェクトGitの `DESIGN_LOG.md`、`docs/requirements/`、`docs/specs/` に残す。
- Codexへの実装依頼は `docs/workflow-design-implementation.md` のテンプレートに従う。

## MiniPC 構築・運用

- 実行機: 常時起動のWindows MiniPC。
- ノートPCはWSL2またはリモートデスクトップでMiniPCへ接続する。
- multi-agent-shogun、Codex、Memory MCP、作業リポジトリはMiniPCに集約する。

初期構築チェックリスト:

- [ ] WSL2セットアップ
- [ ] multi-agent-shogun clone / install / shutsujin
- [ ] Claude / Codex CLIのOAuthログイン
- [ ] Bypass Permissions承認
- [ ] Memory MCP稼働確認
- [ ] 各リポジトリのclone
- [ ] GitHub認証設定

## バックアップ / SPOF対策

MiniPC 1台に集約するため、故障時に全停止するリスクがある。

- 全リポジトリをこまめにGitHubへpushする。
- `.env`、OAuth token、Memory MCPデータ、Shogun `config/settings.yaml` は定期バックアップ対象とする。
- バックアップ先と頻度はMiniPC構築時に確定する。

## リモートアクセスのセキュリティ

- ポートを直接インターネットへ開けない。
- 可能ならTailscaleなどのプライベート網経由で接続する。

## Google Account

Google系作業は原則として次のアカウントを使う。

```text
s.jinnouchi@yumekango.com
```

別アカウントが表示された場合は作業を止め、ユーザーに確認する。

## Secrets

以下はGitHub、Markdown、チャットに保存しない。

- APIキー
- OAuth refresh token
- GitHub token
- Google認証情報
- パスワード
- Supabase / Cloudflare / LINE / Square / ChatWork の実値token
