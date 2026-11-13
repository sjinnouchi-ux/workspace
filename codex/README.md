# Codex 運用フォルダ

Codex専用の作業ルール、操作メモ、引き継ぎ情報を管理するフォルダです。

## 目的

- Claude Coworkとは異なるCodex側の操作手順を明確に分ける
- GAS、Google API、GitHub、ブラウザ操作のCodex向け運用を記録する
- Codexが実施した調査・設定・残課題をMarkdownで継続管理する

## 現在の方針

- Python、Git、ローカルファイル操作はCodexから直接実行する
- GitHub操作はCodexから `git pull/add/commit/push` まで完結する
- 外部接続は実際に使用するconnector/CLI/MCP/browserの境界で確認し、過去の接続制約を現在の全PCへ一般化しない
- 秘密情報、OAuthコード、トークン、認証JSONの中身はMarkdownに記録しない

## ファイル

| ファイル | 内容 |
|---------|------|
| [CODEX_DESKTOP_STARTUP.md](./CODEX_DESKTOP_STARTUP.md) | 全PC共通のオンライン起動手順とローカル作業場の完了条件 |
| [CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md](./CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md) | Codex Desktopのパーソナライズへ設定する共通bootstrap文面 |
| [connection-authentication-boundaries.md](./connection-authentication-boundaries.md) | connector/CLI/MCP/browser/Remoteの誤判定防止 |
| [../docs/history/workspace-pr-cleanup-2026-11-13/README.md](../docs/history/workspace-pr-cleanup-2026-11-13/README.md) | 旧PR原版・frontend-design出典/licenseの保存索引（今回installなし） |
| [gas_browser_operation.md](./gas_browser_operation.md) | CodexでGASをブラウザ操作する手順 |
| [2026-07-11-project-entrypoint-inventory.md](./2026-07-11-project-entrypoint-inventory.md) | GitHub・ローカルGit・Codex trusted path・AGENTS入口の全棚卸し |
| [work_log.md](./work_log.md) | Codex専用作業ログ |

## 運用ルール

1. 各PCのカスタム指示はオンライン起動手順へのbootstrapだけを持つ
2. Codex固有の共通操作方針はこのフォルダに記録する
3. 実作業の結果は `codex/work_log.md` に追記する
4. ワークスペース全体の判断は日付付きreportと `codex/work_log.md` に記録する。旧 `claude_log.md` は履歴として保持する
5. 作業後は必ずGitHubへpushし、ローカルだけの記録を残さない
