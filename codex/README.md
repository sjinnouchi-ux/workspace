# Codex 運用フォルダ

Codex専用の作業ルール、操作メモ、引き継ぎ情報を管理するフォルダです。

## 目的

- Claude Coworkとは異なるCodex側の操作手順を明確に分ける
- GAS、Google API、GitHub、ブラウザ操作のCodex向け運用を記録する
- Codexが実施した調査・設定・残課題をMarkdownで継続管理する

## 現在の方針

- Python、Git、ローカルファイル操作はCodexから直接実行する
- GitHub操作はCodexから `git pull/add/commit/push` まで完結する
- GASのCLI操作は `clasp` 認証制約が残っているため、当面はCodex内ブラウザでApps Scriptエディタを操作する
- 秘密情報、OAuthコード、トークン、認証JSONの中身はMarkdownに記録しない

## ファイル

| ファイル | 内容 |
|---------|------|
| [CODEX_DESKTOP_STARTUP.md](./CODEX_DESKTOP_STARTUP.md) | 全PC共通のオンライン起動手順とローカル作業場の完了条件 |
| [CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md](./CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md) | Codex Desktopのパーソナライズへ設定する共通bootstrap文面 |
| [skills/](./skills/) | 複数PCで共有するCodexスキルのGit正本、ライセンス、取得元 |
| [gas_browser_operation.md](./gas_browser_operation.md) | CodexでGASをブラウザ操作する手順 |
| [official_line_ai_integration.md](./official_line_ai_integration.md) | 公式LINE AI連携の現状整理・テスト環境方針 |
| [2026-07-11-project-entrypoint-inventory.md](./2026-07-11-project-entrypoint-inventory.md) | GitHub・ローカルGit・Codex trusted path・AGENTS入口の全棚卸し |
| [work_log.md](./work_log.md) | Codex専用作業ログ |

## 運用ルール

1. 各PCのカスタム指示はオンライン起動手順へのbootstrapだけを持つ
2. Codex固有の共通操作方針はこのフォルダに記録する
3. 実作業の結果は `codex/work_log.md` に追記する
4. ワークスペース全体に関わる作業はルートの `claude_log.md` にも記録する
5. 作業後は必ずGitHubへpushし、ローカルだけの記録を残さない
