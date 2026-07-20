# claude/

Claude関連の共通運用の置き場です。`codex/` と対称の役割を持ちます。

## 運用の全体像

| 主体 | 環境 | 役割 | Gitへの反映経路 |
|---|---|---|---|
| Claude Code（クラウドセッション） | claude.ai/code 環境 `yumekango-standard`（2PC＋スマホ共有） | 設計・調査・レビュー、軽微なPR作業 | セッション自身が専用branch/PRをpush |
| Claude CLI | Shogun（MiniPC WSL2） | Shogun配下のClaude割当役職 | Shogun専用branch（既存規則） |
| Claude Desktop | 両PC個別（同期しない） | 相談・分析・作業レポート作成 | Drive受信箱経由でCodexが統合 |
| Codex Desktop | 両PC（既存運用） | 実装・検証・デプロイ＋レポート統合 | 既存のCleanup Gate |

- 各PCへのClaude Code個別インストールは行わない。共有作業場はクラウドセッション（VMは使い捨て、正本はGitHub）。
- 秘密値はクラウド環境定義・レポート・Markdownのいずれにも置かない（`MCP.md` の共通ルールどおり）。

## Files

| File | Role |
|---|---|
| `CLAUDE_CODE_STARTUP.md` | Claude Code（クラウドセッション / Shogun配下CLI）が作業開始時にGitHub `main` から取得するオンライン正本 |
| `CLOUD_ENVIRONMENT.md` | クラウド環境定義 `yumekango-standard` の仕様書・再作成手順・セッション運用ルール |
| `REPORT_INTAKE.md` | Claude Desktopレポート → Drive受信箱 → Codex統合のオペレーション正本 |
