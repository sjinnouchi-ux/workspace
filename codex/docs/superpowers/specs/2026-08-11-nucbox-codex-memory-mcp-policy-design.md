# NUCBOX_K8_PLUS Codex Memory MCP Policy Design

## Purpose

`NUCBOX_K8_PLUS` の Windows Codex Desktop で、過去に確認された失敗と改善策を再利用し、同じ調査や誤修正を繰り返さない。

このポリシーはノートPCへ同じメモリが存在すると仮定しない。Memory MCP は補助情報であり、GitHub の既定ブランチ、`AGENTS.md`、`PROJECTS.md`、Primary Docs を正本とする既存の起動順序を変更しない。

## Scope

- 対象: host `NUCBOX_K8_PLUS` の Windows Codex Desktop
- MCP server: `shogun_memory`
- runtime: Windows 側のローカル STDIO MCP
- storage: Windows 側の永続ファイル
- 対象外: WSL2、tmux、Shogun runtime、ノートPC、他PCへの同期

## Task-start flow

1. 現行の共通起動手順どおり、GitHub `main` の `CODEX_DESKTOP_STARTUP.md` と `PROJECTS.md` を先に取得する。
2. Canonical Entry、既定ブランチ、対象repoの `AGENTS.md`、Primary Docsを確認する。
3. その後に限り、`shogun_memory` で Canonical repo名、component名、failure patternを対象に絞って検索する。
4. 関連する `VerifiedFailurePattern` があれば、症状、確定原因、検証済み修正、証拠参照を読んでから作業する。
5. GitHub正本とメモリが矛盾する場合はGitHubを採用し、メモリを根拠に正本確認を省略しない。

メモリ検索が利用不能または結果0件でも、GitHub正本を確認できる限りタスクは継続する。利用不能だった事実だけを報告し、Memory MCPを必須gateにしない。

## Recording flow

タスク完了時、再発可能性と再利用価値があり、原因が確認され、修正後の検証が通った失敗だけを記録する。

記録単位は `VerifiedFailurePattern` entity とし、次の情報だけを保持する。

- host scope: `NUCBOX_K8_PLUS Windows Codex Desktop`
- Canonical repoまたは共通運用area
- component
- sanitized symptom
- confirmed root cause
- verified fix
- GitHub commit、PR、test result等のevidence reference
- verification date

同じpatternが存在する場合は重複entityを作らず、既存entityへ新しい検証結果を追記する。過去の記録と異なる結果は上書きせず、後続の検証として追記する。

## Exclusions

次は記録しない。

- 原因未確定、推測段階、一時的または再現不能な失敗
- 秘密値、OAuth code、token、credential、認証JSON、`.env` 内容
- 生ログ、生pane、生queue、生report、例外全文
- 個人識別情報、不要なローカル絶対path、環境変数値
- タスク本文や会話全文

## Configuration

GitHub正本の `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` に、`NUCBOX_K8_PLUS` でのみ適用される条件付きブロックを追加する。このPCの `~/.codex/AGENTS.md` に同じブロックを反映する。

ノートPCでは、このブロックを自動適用せず、同一のMemory MCPデータが存在すると推測しない。

## Verification

1. GitHub正本とローカル `~/.codex/AGENTS.md` の追加ブロックがbyte一致することを確認する。
2. 新しいCodex Desktopタスクを開始し、AGENTSは起動時読込であることを前提にする。
3. 新タスクでGitHub正本確認がMemory MCP検索より先に行われることを確認する。
4. `shogun_memory` の存在しないprobe queryを1回実行し、書込みなしで接続成功を確認する。
5. test code、WSL、Shogun runtime、GitHub以外の外部サービスは変更しない。

