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

ShogunはWSL2 Linux + WebUI上で、Codex Desktopと設定・認証・session・Drive領域を共有しない「GitHub境界連携方式」として別運用します。Shogun実装・設定は明示的なShogun作業でのみ扱い、通常のCodex Desktop交通整理の対象にしないでください。

NUCBOX_K8_PLUSでは、Shogunは実Windowsユーザー jinnouchi のWSL2 Ubuntuにあります。Codex隔離ユーザーから `wsl.exe --list` が空に見えても未インストールと判定せず、実ユーザー環境での実行許可を取得して確認してください。入口は `wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun`、tmux sessionは `shogun` と `multiagent`、WebUIは `http://127.0.0.1:8790/` です。`ShogunUbuntu` は使用しません。別PCでローカル実体が見つからない場合も、Shogun全体が未導入・消失したとは判定しないでください。秘密設定、tmux pane、生queue、生report、生ログは読み取り・出力しないでください。

<!-- BEGIN CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->
### Codex read-only diagnostics limited exception

The preceding prohibition remains in force. Immediately before each diagnostic
invocation, Codex must fetch GitHub `main` raw
`docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md`,
validate its single marked schema-version-1 JSON registry and exactly one active
deployment, then compare that record's source SHA-256 with the returned
`tool.source_sha256`.

Only this complete command is eligible for a persistent argv-prefix permission:

`wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-diagnostics summary`

The installed mode-`0555` snapshot may locally aggregate only its fixed,
allowlisted Git/tmux/process/filesystem metadata and the counts of its four fixed
watcher-log substrings from at most the final 1,048,576 bytes. Codex receives
only schema-version-1 JSON. It does not directly read runtime files, logs, or
panes.

Before using any diagnostic field, Codex must require exit 0 and independently
validate ASCII-only bytes plus the complete nested schema, exact key order,
session/agent cardinality, enums, issue severity, count/state/applicability
cross-field invariants, and a recomputed `overall` value.

Do not persist a shorter `wsl.exe`, `bash -lc`, `python3`, or repo-script prefix.
`cat`, `grep`, YAML bodies, log lines, pane capture, arbitrary paths, sessions,
agents, regexes, shell commands, other scripts, suffix arguments, environment
overrides, starts, stops, restarts, repairs, and writes remain forbidden.

GitHub provenance retrieval or validation failure, no active deployment,
multiple active deployments, and source-hash mismatch are
`diagnostic_provenance_untrusted`. A nonzero exit, empty/non-JSON/partial output,
nonempty stderr, or execution of 10 seconds or more is `diagnostic_process_failed`. In both cases, do
not trust diagnostic fields and do not use any raw or direct-read fallback.
Snapshot placement or update is a separate, explicitly approved Shogun
deployment task and is not part of this exception.
<!-- END CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->
```

## Verification

設定後に新しいCodexタスクを開始し、次を依頼します。

```text
共通起動手順とPROJECTS.mdをGitHub mainから取得し、取得したworkspace commit SHAと、現在登録されているCanonical Entryの件数を報告してください。ローカルcloneはまだ作らないでください。
```

成功条件:

- raw GitHub URLを取得できる
- `sjinnouchi-ux/workspace` のcommit SHAを報告できる
- `PROJECTS.md` のCanonical Entryを読める
- 同名ローカルフォルダへ先に移動しない
- Before every fixed diagnostic invocation, GitHub main has one valid active deployment and its source SHA-256 matches `tool.source_sha256`.
- The complete command exits 0, returns one fully schema-valid version-1 ASCII JSON object, has empty stderr, and finishes in under 10 seconds; `overall=degraded|unavailable` is not a process failure.
- Free text, pane/YAML/log bodies, paths, PID, command line, remote URL, exact runtime sizes, and runtime hashes are absent.
- Provenance/process failure never triggers a raw fallback, repo-script execution, shorter WSL permission, or direct runtime read.
