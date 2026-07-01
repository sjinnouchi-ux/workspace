# Shogun（仮） Work Log

## 2026-06-25

- `shogun-lab/` を新規作成。
- 目的を「Shogunで設計したMarkdownをCodexが実行できるように引き継ぐ中継プロジェクト」として定義。
- Shogun設計MDの保存先を `handoffs/`、Codex実行結果の保存先を `codex-execution/`、テンプレートを `templates/` に分離。
- 既存プロジェクトの実装コードとは干渉しないよう、トップレベルの独立フォルダとして配置。
- 直近のShogunローカル導入状況は `docs/setup_status.md` に記録。
- 旧運用ではルートのJSONインデックスとNotion用CSVに `shogun-lab` を追加していた。
- NotionプロジェクトDBに `Shogun（仮）` 行を作成。
  - URL: https://app.notion.com/p/38a150a94747818fbd30db6760d4f612
- Shogun本体の `shutsujin_departure.sh` を足軽3体構成に合わせて調整。
  - 9ペイン固定生成をやめ、`settings.yaml` の足軽数に応じて `家老 + 足軽 + 軍師` のペインを作成。
  - 2026-06-25時点では5ペイン構成。
  - 起動バナーと布陣図も3体/5ペイン表示に更新。
- `./shutsujin_departure.sh -S` で通常起動を再確認。
  - Codex MCP Health Check: 足軽3 + 軍師 = 4ペイン正常。
  - 起動後メモリ: WSL側 `used 938MiB`。
  - テスト後、tmuxセッションとwatcherは停止済み。
- Claude初回テーマは Dark mode で確定。
- 残タスクは本人認証が必要な Claude Code ログインと Codex CLI ChatGPTサインイン。
- ユーザー操作によりClaude Codeログイン完了。
  - `~/.claude/.credentials.json` の作成を確認。
  - tmuxセッションは残っていないことを確認。
  - 次はShogun通常起動後、全ペインがready状態になることを最終確認する。
