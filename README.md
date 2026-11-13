# workspace

各プロジェクトのGitHub正本と共通運用への入口を管理するリポジトリです。詳細な設計、実装、作業記録は各Canonical repoへ保存します。

## 作業開始

1. GitHub mainの[共通起動手順](codex/CODEX_DESKTOP_STARTUP.md)を読む。
2. [PROJECTS.md](PROJECTS.md)でCanonical EntryとPrimary Docsを確定する。
3. 対象repoの既定ブランチ、AGENTS.md、Primary Docsを確認する。
4. 必要な場合だけタスク専用clone/worktreeを作る。ローカルフォルダやMemoryを先に正本にしない。

## 現行の役割

- Codex Desktopが唯一のオーケストレーターとして、設計、実装、検証、GitHub反映を担当する。
- Windows Memory MCPは、GitHub確認後に参照するhost限定の補助知識。別PCと同一とは推測しない。
- WSL2 Claude CLIは、利用者が監査を求めた場合だけ、[development-environment](https://github.com/sjinnouchi-ux/development-environment)の固定runnerによる一回限りのread-only監査へ使用する。
- 旧Shogun、WebUI、固定Ops、diagnostics、break-glass、parallel Shogunと旧repoは退役済み。起動、修復、再配備、新task配送を行わない。

詳しい責務と保存先は[設計・実装・監査の分担](docs/workflow-design-implementation.md)を参照してください。退役前の記述は[移行記録](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/MIGRATION_MANIFEST.md)と日付付き履歴として扱います。

## 共通の入口

| 用途 | 正本 |
|---|---|
| プロジェクトの所在・現役/凍結/退役状態 | [PROJECTS.md](PROJECTS.md) |
| 共通起動・完了・ローカル整理 | [Codex Desktop Startup](codex/CODEX_DESKTOP_STARTUP.md) |
| 承認・本人操作・継続 | [共通方針](codex/AGENT_APPROVAL_POLICY.md) |
| GitHub引継ぎ・固定SHA・保存確認 | [Git Handoff Protocol](GIT_HANDOFF_PROTOCOL.md) |
| Actions・検証コスト | [共通方針](codex/GITHUB_ACTIONS_POLICY.md) |
| MCP・外部接続・hostの境界 | [MCP.md](MCP.md) |
| Codex共通手順と作業ログ | [codex/](codex/README.md) |
| Claudeからの明示依頼されたレポート取込み | [Report intake](claude/REPORT_INTAKE.md) |

秘密値、OAuthコード、token、認証JSON、.env内容はチャットやGitHubへ保存しません。未登録プロジェクトは同名ローカルフォルダへ推測で割り当てず、対象を確認します。

[2026-11-13 入口文書・旧PR整理記録](docs/reports/2026-11-13-workspace-entrypoint-pr-cleanup.md)
