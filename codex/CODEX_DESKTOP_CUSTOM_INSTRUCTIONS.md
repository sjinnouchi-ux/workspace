# Codex Desktop Custom Instructions

## Purpose

Codex Desktopの `Settings > Personalization > Custom instructions` に設定する共通文面です。Codexではこの内容が各PCのグローバル `~/.codex/AGENTS.md` として扱われます。

Official reference: https://learn.chatgpt.com/docs/personalize

全文の運用規則を各PCへ複製せず、GitHub `main` のオンライン正本へ案内するbootstrapだけを置きます。

## Paste This Text

```text
各タスク開始時、ローカルフォルダ、過去のclone、Codexメモリをプロジェクトの正本として先に使用しないでください。

最初に、GitHub main上の次の共通起動手順を必ず取得し、最新版に従ってください。
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md

次に、次のオンライン台帳から対象プロジェクトのCanonical Entryを確定してください。
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md

対象GitHub repoの既定ブランチ、AGENTS.md、PROJECTS.md記載のPrimary Docsを確認してから作業してください。

URLを取得できない、GitHubのprivate repoへ認証できない、対象プロジェクトを特定できない場合は、同名ローカルフォルダを推測で使わず、作業を停止して不足事項を報告してください。

実装はタスク専用のローカルclone/worktreeで行って構いません。完了時は必要な変更と作業ログをGitHubへ反映し、未コミット、未push、ローカル専用情報がないことを確認してからローカル作業場を整理してください。

秘密値、OAuthコード、token、認証JSON、.envの中身をチャットやGitHubへ表示・保存しないでください。

<!-- BEGIN NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V2 -->
### NUCBOX_K8_PLUS Windows Codex Desktop Memory MCP

この規則は host `NUCBOX_K8_PLUS` のWindows Codex Desktopにだけ適用します。ノートPC、WSL2、他PCに同じMemory MCP設定・保存内容があると推測しないでください。

GitHub正本、Canonical Entry、対象repoの既定ブランチ・AGENTS.md・Primary Docsを確認した後に限り、`development_memory` をCanonical repo名とcomponent名で検索し、関連する `VerifiedFailurePattern` のsanitized symptom、confirmed root cause、verified fix、evidence referenceを確認してください。GitHubと矛盾する場合はGitHubを優先し、Memory MCPが利用不能または該当0件でもGitHub正本を確認できる限り作業を継続してください。

タスク完了時、再発可能性と再利用価値があり、原因が確認され、修正後の検証が通った失敗だけを `VerifiedFailurePattern` として記録してください。host scope、Canonical repoまたは共通運用area、component、sanitized symptom、confirmed root cause、verified fix、GitHub commit・PR・test result等のevidence reference、verification dateだけを保持してください。同じpatternは重複entityを作らず、後続検証を追記してください。

原因未確定、推測段階、一時的または再現不能な失敗、秘密値、OAuth code、token、credential、認証JSON、.env内容、生ログ、生pane、生queue、生report、例外全文、個人識別情報、不要なローカル絶対path、環境変数値、タスク本文や会話全文は記録しないでください。
<!-- END NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V2 -->

Codex Desktopを唯一のオーケストレーターとします。WSL2 Claude CLIは、利用者が監査を求めた場合だけprivate repo `sjinnouchi-ux/development-environment` の固定runnerから一回限りのread-only監査として使用し、task配送、常設worker、変更、retry、fallbackには使用しません。

旧Shogun runtime、WebUI、固定Ops、diagnostics、break-glass、Native Windows parallel Shogunは退役対象です。新規taskを配送せず、start、restart、repair、再配備、旧repoのCanonical Entry利用を行わないでください。移行・削除の正本は `sjinnouchi-ux/development-environment` です。
```

## Verification

設定後に新しいCodexタスクを開始し、次を依頼します。

```text
共通起動手順とPROJECTS.mdをGitHub mainから取得し、取得したworkspace commit SHA、開発環境のCanonical Entry、NUCBOX_K8_PLUSでのMemory MCP名、Claude監査の役割、旧Shogunの状態を報告してください。ローカルcloneはまだ作らず、メモリへの書込みもしないでください。
```

成功条件:

- raw GitHub URLを取得できる
- `sjinnouchi-ux/workspace` のcommit SHAを報告できる
- 開発環境のCanonical Entryをprivate `sjinnouchi-ux/development-environment` と判定できる
- GitHub確認後にだけ `development_memory` を補助参照する
- Claude CLIを一回限りのread-only監査と説明できる
- 旧Shogunへtaskを配送または起動しない
- 同名ローカルフォルダへ先に移動しない
