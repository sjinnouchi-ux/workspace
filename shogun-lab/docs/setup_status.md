# Shogun（仮） Setup Status

最終確認日: 2026-06-25

## ローカル実体

- Windows path: `C:\tools\multi-agent-shogun`
- WSL path: `/mnt/c/tools/multi-agent-shogun`
- WSL user: `yumekango`

## 確認済み

- WSL側 Claude Code CLI: `2.1.191`
- WSL側 Codex CLI: `codex-cli 0.142.2`
- Shogun設定: 足軽3体構成
- 足軽: `ashigaru1`, `ashigaru2`, `ashigaru3`
- 軍師: `gunshi`
- 通知常駐: `ntfy_topic: ""`
- 起動確認: `./shutsujin_departure.sh -S`
- MCP Health Check: Codex 4ペイン正常
- 起動テスト後の状態: tmuxセッション停止済み
- `shutsujin_departure.sh` の表示とtmux生成を足軽3体構成に合わせて調整
  - multiagent: 家老 + 足軽3 + 軍師 = 5ペイン
  - 起動バナー: 足軽3名表示
  - 布陣図: 5ペイン表示
- 5ペイン構成で通常起動を再確認
  - MCP Health Check: Codex 4ペイン正常
  - 起動中メモリ目安: WSL側 `used 938MiB`
- Claude初回テーマ選択は Dark mode で確定済み
- Claude Code 認証済み
  - `~/.claude/.credentials.json` 作成確認: 2026-06-25 18:19

## 未完了

- Shogun通常起動後に、将軍・家老・足軽・軍師が全員ready状態になることの最終確認
- `inotifywait` は未導入。必要になった場合は WSL 側で `sudo apt install inotify-tools` が必要

## 起動メモ

```bash
cd /mnt/c/tools/multi-agent-shogun
./shutsujin_departure.sh -S
tmux attach-session -t shogun
```

停止:

```bash
tmux kill-session -t shogun
tmux kill-session -t multiagent
```
